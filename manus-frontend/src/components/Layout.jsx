import React, { useState } from 'react'
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import {
  LayoutDashboard,
  CheckSquare,
  Bot,
  FileText,
  User,
  Settings,
  LogOut,
  Menu,
  Zap,
  CreditCard,
} from 'lucide-react'

const Layout = () => {
  const { user, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const navigation = [
    { name: 'Dashboard', href: '/app/dashboard', icon: LayoutDashboard },
    { name: 'Tasks', href: '/app/tasks', icon: CheckSquare },
    { name: 'Agents', href: '/app/agents', icon: Bot },
    { name: 'Content', href: '/app/content', icon: FileText },
    { name: 'Profile', href: '/app/profile', icon: User },
    { name: 'Settings', href: '/app/settings', icon: Settings },
  ]

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const getSubscriptionColor = (type) => {
    switch (type) {
      case 'premium': return 'bg-blue-500'
      case 'enterprise': return 'bg-purple-500'
      default: return 'bg-gray-500'
    }
  }

  const Sidebar = ({ mobile = false }) => (
    <div className={`flex flex-col h-full ${mobile ? 'w-full' : 'w-64'}`}>
      {/* Logo */}
      <div className="flex items-center px-6 py-4 border-b">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <Zap className="h-5 w-5 text-white" />
          </div>
          <span className="text-xl font-bold">Manus AI</span>
        </div>
      </div>

      {/* User info */}
      <div className="px-6 py-4 border-b">
        <div className="flex items-center space-x-3">
          <Avatar className="h-10 w-10">
            <AvatarImage src={user?.avatar_url} />
            <AvatarFallback>
              {user?.first_name?.[0]}{user?.last_name?.[0]} || {user?.username?.[0]?.toUpperCase()}
            </AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">
              {user?.first_name && user?.last_name 
                ? `${user.first_name} ${user.last_name}`
                : user?.username
              }
            </p>
            <div className="flex items-center space-x-2">
              <Badge 
                variant="secondary" 
                className={`text-xs ${getSubscriptionColor(user?.subscription_type)} text-white`}
              >
                {user?.subscription_type?.toUpperCase()}
              </Badge>
              <span className="text-xs text-muted-foreground">
                {user?.credits_balance} credits
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-4 space-y-1">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href
          return (
            <Link
              key={item.name}
              to={item.href}
              onClick={() => mobile && setSidebarOpen(false)}
              className={`flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:text-foreground hover:bg-muted'
              }`}
            >
              <item.icon className="mr-3 h-5 w-5" />
              {item.name}
            </Link>
          )
        })}
      </nav>

      {/* Upgrade prompt for free users */}
      {user?.subscription_type === 'free' && (
        <div className="p-4 m-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border">
          <div className="flex items-center space-x-2 mb-2">
            <CreditCard className="h-4 w-4 text-blue-600" />
            <span className="text-sm font-medium text-blue-900">Upgrade to Premium</span>
          </div>
          <p className="text-xs text-blue-700 mb-3">
            Get more credits, advanced agents, and priority support.
          </p>
          <Button size="sm" className="w-full">
            Upgrade Now
          </Button>
        </div>
      )}
    </div>
  )

  return (
    <div className="flex h-screen bg-background">
      {/* Desktop Sidebar */}
      <div className="hidden lg:flex lg:flex-shrink-0">
        <div className="flex flex-col w-64 border-r bg-card">
          <Sidebar />
        </div>
      </div>

      {/* Mobile Sidebar */}
      <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
        <SheetContent side="left" className="p-0 w-64">
          <Sidebar mobile />
        </SheetContent>
      </Sheet>

      {/* Main Content */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Top Navigation */}
        <header className="flex items-center justify-between px-6 py-4 border-b bg-card">
          <div className="flex items-center space-x-4">
            <Sheet>
              <SheetTrigger asChild>
                <Button variant="ghost" size="sm" className="lg:hidden">
                  <Menu className="h-5 w-5" />
                </Button>
              </SheetTrigger>
              <SheetContent side="left" className="p-0 w-64">
                <Sidebar mobile />
              </SheetContent>
            </Sheet>
            
            <h1 className="text-2xl font-semibold">
              {navigation.find(item => item.href === location.pathname)?.name || 'Manus AI'}
            </h1>
          </div>

          <div className="flex items-center space-x-4">
            {/* Credits display */}
            <div className="hidden sm:flex items-center space-x-2 px-3 py-1 bg-muted rounded-full">
              <Zap className="h-4 w-4 text-yellow-500" />
              <span className="text-sm font-medium">{user?.credits_balance}</span>
            </div>

            {/* User menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                  <Avatar className="h-8 w-8">
                    <AvatarImage src={user?.avatar_url} />
                    <AvatarFallback>
                      {user?.first_name?.[0]}{user?.last_name?.[0]} || {user?.username?.[0]?.toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56" align="end" forceMount>
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none">
                      {user?.first_name && user?.last_name 
                        ? `${user.first_name} ${user.last_name}`
                        : user?.username
                      }
                    </p>
                    <p className="text-xs leading-none text-muted-foreground">
                      {user?.email}
                    </p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => navigate('/app/profile')}>
                  <User className="mr-2 h-4 w-4" />
                  Profile
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => navigate('/app/settings')}>
                  <Settings className="mr-2 h-4 w-4" />
                  Settings
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout}>
                  <LogOut className="mr-2 h-4 w-4" />
                  Log out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default Layout

