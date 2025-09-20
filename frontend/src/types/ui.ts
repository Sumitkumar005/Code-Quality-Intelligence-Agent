// UI Component Types
export interface NavItem {
  title: string
  href: string
  icon?: string
  badge?: string | number
  children?: NavItem[]
  disabled?: boolean
  external?: boolean
}

export interface BreadcrumbItem {
  title: string
  href?: string
  current?: boolean
}

export interface TableColumn<T = any> {
  key: string
  title: string
  sortable?: boolean
  filterable?: boolean
  width?: string | number
  align?: 'left' | 'center' | 'right'
  render?: (value: any, record: T, index: number) => React.ReactNode
  filterType?: 'text' | 'select' | 'date' | 'number'
  filterOptions?: { value: string; label: string }[]
}

export interface TableProps<T = any> {
  data: T[]
  columns: TableColumn<T>[]
  loading?: boolean
  pagination?: {
    current: number
    pageSize: number
    total: number
    showSizeChanger?: boolean
    showQuickJumper?: boolean
    showTotal?: (total: number, range: [number, number]) => string
  }
  rowSelection?: {
    selectedRowKeys: string[]
    onChange: (selectedRowKeys: string[]) => void
  }
  onRow?: (record: T, index: number) => {
    onClick?: () => void
    onDoubleClick?: () => void
    onContextMenu?: () => void
  }
  size?: 'small' | 'middle' | 'large'
  bordered?: boolean
  scroll?: { x?: number | string; y?: number | string }
}

export interface ModalProps {
  title?: string
  visible: boolean
  onCancel: () => void
  onOk?: () => void
  confirmLoading?: boolean
  width?: string | number
  footer?: React.ReactNode
  closable?: boolean
  maskClosable?: boolean
  destroyOnClose?: boolean
  children: React.ReactNode
}

export interface DrawerProps {
  title?: string
  visible: boolean
  onClose: () => void
  width?: string | number
  placement?: 'left' | 'right' | 'top' | 'bottom'
  closable?: boolean
  maskClosable?: boolean
  destroyOnClose?: boolean
  children: React.ReactNode
}

export interface FormProps {
  initialValues?: Record<string, any>
  onSubmit: (values: Record<string, any>) => void | Promise<void>
  onCancel?: () => void
  loading?: boolean
  layout?: 'horizontal' | 'vertical' | 'inline'
  size?: 'small' | 'middle' | 'large'
  children: React.ReactNode
}

export interface CardProps {
  title?: string
  extra?: React.ReactNode
  size?: 'small' | 'default'
  bordered?: boolean
  hoverable?: boolean
  loading?: boolean
  children: React.ReactNode
  onClick?: () => void
}

export interface BadgeProps {
  count?: number
  text?: string
  status?: 'success' | 'processing' | 'default' | 'error' | 'warning'
  color?: string
  size?: 'small' | 'default'
  overflowCount?: number
  showZero?: boolean
}

export interface AlertProps {
  type: 'success' | 'info' | 'warning' | 'error'
  message: string
  description?: string
  closable?: boolean
  onClose?: () => void
  showIcon?: boolean
  banner?: boolean
}

export interface NotificationProps {
  type: 'success' | 'info' | 'warning' | 'error'
  title: string
  message?: string
  duration?: number
  placement?: 'topLeft' | 'topRight' | 'bottomLeft' | 'bottomRight'
}

export interface TooltipProps {
  title: string
  placement?: 'top' | 'left' | 'right' | 'bottom' | 'topLeft' | 'topRight' | 'bottomLeft' | 'bottomRight'
  trigger?: 'hover' | 'focus' | 'click'
  children: React.ReactNode
}

export interface DropdownProps {
  trigger: ('click' | 'hover' | 'contextMenu')[]
  overlay: React.ReactNode
  placement?: 'bottomLeft' | 'bottomRight' | 'topLeft' | 'topRight'
  children: React.ReactNode
}

export interface MenuProps {
  mode?: 'horizontal' | 'vertical' | 'inline'
  theme?: 'light' | 'dark'
  selectedKeys?: string[]
  openKeys?: string[]
  onSelect?: (selectedKeys: string[]) => void
  onOpenChange?: (openKeys: string[]) => void
  children: React.ReactNode
}

export interface TabsProps {
  activeKey?: string
  onChange?: (activeKey: string) => void
  type?: 'line' | 'card' | 'editable-card'
  size?: 'small' | 'default' | 'large'
  tabPosition?: 'top' | 'right' | 'bottom' | 'left'
  children: React.ReactNode
}

export interface ButtonProps {
  type?: 'primary' | 'default' | 'dashed' | 'text' | 'link'
  size?: 'small' | 'middle' | 'large'
  loading?: boolean
  disabled?: boolean
  danger?: boolean
  ghost?: boolean
  block?: boolean
  icon?: React.ReactNode
  onClick?: () => void
  children?: React.ReactNode
}

export interface InputProps {
  type?: 'text' | 'password' | 'email' | 'number' | 'tel' | 'url'
  size?: 'small' | 'middle' | 'large'
  placeholder?: string
  disabled?: boolean
  readOnly?: boolean
  allowClear?: boolean
  showCount?: boolean
  maxLength?: number
  prefix?: React.ReactNode
  suffix?: React.ReactNode
  onChange?: (value: string) => void
  onPressEnter?: () => void
}

export interface SelectProps {
  size?: 'small' | 'middle' | 'large'
  placeholder?: string
  disabled?: boolean
  loading?: boolean
  allowClear?: boolean
  showSearch?: boolean
  mode?: 'multiple' | 'tags'
  options: { value: string; label: string; disabled?: boolean }[]
  onChange?: (value: string | string[]) => void
}

export interface DatePickerProps {
  size?: 'small' | 'middle' | 'large'
  placeholder?: string
  disabled?: boolean
  allowClear?: boolean
  showTime?: boolean
  format?: string
  onChange?: (date: Date | null) => void
}

export interface LoadingProps {
  size?: 'small' | 'middle' | 'large'
  spinning?: boolean
  tip?: string
  children?: React.ReactNode
}

export interface ProgressProps {
  percent: number
  status?: 'success' | 'exception' | 'normal' | 'active'
  type?: 'line' | 'circle' | 'dashboard'
  strokeColor?: string
  trailColor?: string
  showInfo?: boolean
  size?: 'small' | 'default'
}

export interface AvatarProps {
  size?: 'small' | 'middle' | 'large' | number
  shape?: 'circle' | 'square'
  src?: string
  alt?: string
  children?: React.ReactNode
}

export interface TagProps {
  color?: string
  closable?: boolean
  onClose?: () => void
  children: React.ReactNode
}

export interface StatisticProps {
  title?: string
  value: string | number
  prefix?: React.ReactNode
  suffix?: React.ReactNode
  precision?: number
  valueStyle?: Record<string, any>
}

export interface TimelineProps {
  mode?: 'left' | 'alternate' | 'right'
  pending?: string | React.ReactNode
  reverse?: boolean
  children: React.ReactNode
}

export interface CollapseProps {
  accordion?: boolean
  activeKey?: string | string[]
  onChange?: (key: string | string[]) => void
  ghost?: boolean
  children: React.ReactNode
}

export interface TreeProps {
  treeData: TreeNode[]
  defaultExpandAll?: boolean
  expandedKeys?: string[]
  onExpand?: (expandedKeys: string[]) => void
  selectedKeys?: string[]
  onSelect?: (selectedKeys: string[]) => void
  checkable?: boolean
  checkedKeys?: string[]
  onCheck?: (checkedKeys: string[]) => void
}

export interface TreeNode {
  key: string
  title: string
  children?: TreeNode[]
  isLeaf?: boolean
  icon?: React.ReactNode
  disabled?: boolean
}
