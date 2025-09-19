"""
Code duplication detector for identifying duplicate code blocks.
"""

import os
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from collections import defaultdict
import hashlib

from app.core.logging import get_logger

logger = get_logger(__name__)


class DuplicationDetector:
    """
    Detects code duplication across files in a project.
    """

    def __init__(self):
        self.supported_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go'
        }
        self.min_block_size = 6  # Minimum lines for a code block
        self.min_duplicate_lines = 10  # Minimum lines to consider as duplication

    async def analyze(self, project_path: str, config: Any) -> Dict[str, Any]:
        """
        Analyze project for code duplication.
        """
        logger.info(f"Starting duplication analysis for: {project_path}")

        source_files = self._find_source_files(project_path)
        total_files = len(source_files)

        if total_files < 2:
            return {
                'success': True,
                'issues': [],
                'metrics': {
                    'total_duplicated_lines': 0,
                    'duplication_percentage': 0,
                    'duplicate_blocks': 0
                },
                'files_analyzed': total_files,
                'lines_analyzed': 0,
                'languages': []
            }

        # Extract code blocks from all files
        file_blocks = {}
        total_lines = 0
        languages_found = set()

        for file_path in source_files:
            try:
                blocks, lines, language = await self._extract_code_blocks(file_path)
                file_blocks[file_path] = blocks
                total_lines += lines
                languages_found.add(language)

            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")

        # Find duplicates
        duplicates = self._find_duplicates(file_blocks)

        # Generate issues
        issues = self._generate_duplication_issues(duplicates)

        # Calculate metrics
        metrics = self._calculate_duplication_metrics(duplicates, total_lines)

        return {
            'success': True,
            'issues': issues,
            'metrics': metrics,
            'files_analyzed': total_files,
            'lines_analyzed': total_lines,
            'languages': list(languages_found)
        }

    def _find_source_files(self, project_path: str) -> List[str]:
        """
        Find all source code files in the project.
        """
        source_files = []
        path = Path(project_path)

        for file_path in path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                # Skip common directories
                if not any(part.startswith('.') or part in {'__pycache__', 'venv', 'env', 'node_modules', 'build', 'dist'}
                          for part in file_path.parts):
                    source_files.append(str(file_path))

        return source_files

    async def _extract_code_blocks(self, file_path: str) -> Tuple[List[Dict[str, Any]], int, str]:
        """
        Extract code blocks from a file.
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            lines = content.splitlines()
            line_count = len(lines)

            # Determine language
            language = self._get_language_from_extension(file_path)

            # Extract meaningful code blocks
            blocks = self._extract_blocks(lines, language)

            return blocks, line_count, language

        except Exception as e:
            logger.error(f"Error extracting blocks from {file_path}: {e}")
            return [], 0, 'unknown'

    def _get_language_from_extension(self, file_path: str) -> str:
        """
        Determine programming language from file extension.
        """
        ext = Path(file_path).suffix.lower()
        return self.supported_extensions.get(ext, 'unknown')

    def _extract_blocks(self, lines: List[str], language: str) -> List[Dict[str, Any]]:
        """
        Extract code blocks from lines.
        """
        blocks = []
        current_block = []
        start_line = 0

        # Language-specific comment patterns
        if language == 'python':
            comment_pattern = re.compile(r'^\s*#')
            block_delimiters = {'def ', 'class ', 'if ', 'for ', 'while ', 'with ', 'try:'}
        elif language in ['javascript', 'typescript']:
            comment_pattern = re.compile(r'^\s*//|^\s*/\*|\*/\s*$')
            block_delimiters = {'function ', 'if ', 'for ', 'while ', 'class ', 'try ', 'catch '}
        elif language == 'java':
            comment_pattern = re.compile(r'^\s*//|^\s*/\*|\*/\s*$')
            block_delimiters = {'public ', 'private ', 'protected ', 'class ', 'if ', 'for ', 'while ', 'try '}
        else:
            comment_pattern = re.compile(r'^\s*#|^\s*//')
            block_delimiters = {'function ', 'class ', 'if ', 'for ', 'while '}

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Skip empty lines and comments
            if not line or comment_pattern.match(lines[i]):
                i += 1
                continue

            # Check if this is a block start
            is_block_start = any(line.startswith(delimiter) for delimiter in block_delimiters)

            if is_block_start and current_block:
                # Save previous block
                if len(current_block) >= self.min_block_size:
                    blocks.append({
                        'lines': current_block.copy(),
                        'start_line': start_line,
                        'end_line': i - 1,
                        'hash': self._hash_lines(current_block)
                    })
                current_block = []
                start_line = i

            current_block.append(lines[i])
            i += 1

        # Add final block
        if len(current_block) >= self.min_block_size:
            blocks.append({
                'lines': current_block,
                'start_line': start_line,
                'end_line': i - 1,
                'hash': self._hash_lines(current_block)
            })

        return blocks

    def _hash_lines(self, lines: List[str]) -> str:
        """
        Create a hash for a list of lines.
        """
        # Normalize whitespace and create hash
        normalized = []
        for line in lines:
            # Remove leading/trailing whitespace and normalize internal spaces
            normalized_line = ' '.join(line.split())
            normalized.append(normalized_line)

        content = '\n'.join(normalized)
        return hashlib.md5(content.encode()).hexdigest()

    def _find_duplicates(self, file_blocks: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Find duplicate code blocks across files.
        """
        hash_to_blocks = defaultdict(list)

        # Group blocks by hash
        for file_path, blocks in file_blocks.items():
            for block in blocks:
                hash_to_blocks[block['hash']].append({
                    'file_path': file_path,
                    'block': block
                })

        duplicates = []

        # Find groups with duplicates
        for hash_value, block_list in hash_to_blocks.items():
            if len(block_list) > 1:
                # Check if blocks are substantial enough
                block_size = len(block_list[0]['block']['lines'])
                if block_size >= self.min_duplicate_lines:
                    duplicates.append({
                        'hash': hash_value,
                        'occurrences': block_list,
                        'block_size': block_size,
                        'total_occurrences': len(block_list)
                    })

        return duplicates

    def _generate_duplication_issues(self, duplicates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate issues for code duplication.
        """
        issues = []

        for duplicate in duplicates:
            occurrences = duplicate['occurrences']
            block_size = duplicate['block_size']
            total_occurrences = duplicate['total_occurrences']

            # Determine severity based on duplication extent
            if total_occurrences > 3 or block_size > 50:
                severity = 'high'
            elif total_occurrences > 2 or block_size > 25:
                severity = 'medium'
            else:
                severity = 'low'

            # Create issue for each occurrence (except the first)
            first_occurrence = occurrences[0]
            for i, occurrence in enumerate(occurrences[1:], 1):
                block = occurrence['block']
                file_path = occurrence['file_path']

                issues.append({
                    'type': 'code_duplication',
                    'severity': severity,
                    'title': f'Code Duplication: {block_size} lines duplicated',
                    'description': f'Duplicate code block found in {total_occurrences} locations',
                    'file_path': file_path,
                    'line_start': block['start_line'] + 1,
                    'line_end': block['end_line'] + 1,
                    'confidence': 0.95,
                    'duplicate_hash': duplicate['hash'],
                    'block_size': block_size,
                    'total_occurrences': total_occurrences,
                    'recommendation': 'Consider extracting this code into a shared function or module',
                    'code_snippet': '\n'.join(block['lines'][:5]) + ('\n...' if len(block['lines']) > 5 else ''),
                    'other_locations': [
                        {
                            'file': occ['file_path'],
                            'line_start': occ['block']['start_line'] + 1,
                            'line_end': occ['block']['end_line'] + 1
                        }
                        for occ in occurrences if occ != occurrence
                    ]
                })

        return issues

    def _calculate_duplication_metrics(self, duplicates: List[Dict[str, Any]], total_lines: int) -> Dict[str, Any]:
        """
        Calculate duplication-related metrics.
        """
        total_duplicated_lines = 0
        duplicate_blocks = 0

        for duplicate in duplicates:
            block_size = duplicate['block_size']
            occurrences = duplicate['total_occurrences']

            # Count duplicated lines (each duplicate block contributes to total)
            total_duplicated_lines += block_size * (occurrences - 1)
            duplicate_blocks += 1

        # Calculate duplication percentage
        duplication_percentage = (total_duplicated_lines / total_lines * 100) if total_lines > 0 else 0

        # Calculate duplication score (0-100, lower is better)
        duplication_score = max(0, 100 - duplication_percentage * 2)

        return {
            'total_duplicated_lines': total_duplicated_lines,
            'duplication_percentage': round(duplication_percentage, 2),
            'duplicate_blocks': duplicate_blocks,
            'duplication_score': round(duplication_score, 1),
            'unique_duplicate_hashes': len(duplicates),
            'avg_duplicate_block_size': round(total_duplicated_lines / duplicate_blocks, 1) if duplicate_blocks > 0 else 0
        }

    async def get_duplication_report(self, duplicates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate detailed duplication report.
        """
        return {
            'summary': {
                'total_duplicate_groups': len(duplicates),
                'most_duplicated_block': max(duplicates, key=lambda x: x['total_occurrences']) if duplicates else None
            },
            'details': duplicates
        }
