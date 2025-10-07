'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useTheme } from 'next-themes'
import { useAuthStore } from '@/store/auth-store'
import { Button } from '@/components/ui/button'
import { Avatar } from '@/components/ui/avatar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  User,
  Settings,
  LogOut,
  Shield,
  UserCheck,
  Stethoscope,
  UserCircle,
  Sun,
  Moon
} from 'lucide-react'
import { toast } from 'sonner'

export function UserMenu() {
  const { user, logout, isAuthenticated } = useAuthStore()
  const router = useRouter()
  const { theme, setTheme } = useTheme()
  const [isLoggingOut, setIsLoggingOut] = useState(false)

  if (!isAuthenticated || !user) {
    return (
      <div className="flex gap-2">
        <Button 
          variant="outline" 
          size="sm"
          onClick={() => router.push('/auth/login')}
        >
          Sign In
        </Button>
        <Button 
          size="sm"
          onClick={() => router.push('/auth/register')}
        >
          Sign Up
        </Button>
      </div>
    )
  }

  const handleLogout = async () => {
    try {
      setIsLoggingOut(true)
      logout()
      toast.success('Logged out successfully')
      router.push('/auth/login')
    } catch (error) {
      toast.error('Error logging out')
    } finally {
      setIsLoggingOut(false)
    }
  }

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'doctor':
        return <Stethoscope className="h-4 w-4" />
      case 'admin':
        return <Shield className="h-4 w-4" />
      default:
        return <User className="h-4 w-4" />
    }
  }

  const getRoleLabel = (role: string) => {
    return role.charAt(0).toUpperCase() + role.slice(1)
  }

  const getUserInitials = () => {
    if (user.username) {
      return user.username.substring(0, 2).toUpperCase()
    }
    return user.email.substring(0, 2).toUpperCase()
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="relative h-8 w-8 rounded-full">
          <Avatar className="h-8 w-8">
            <div className="flex h-full w-full items-center justify-center bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-sm font-medium">
              {getUserInitials()}
            </div>
          </Avatar>
        </Button>
      </DropdownMenuTrigger>
      
      <DropdownMenuContent className="w-64" align="end" forceMount>
        <DropdownMenuLabel className="font-normal">
          <div className="flex flex-col space-y-1">
            <div className="flex items-center gap-2">
              <p className="text-sm font-medium leading-none">{user.username}</p>
              <div className="flex items-center gap-1">
                {getRoleIcon(user.role)}
                <span className="text-xs text-muted-foreground">
                  {getRoleLabel(user.role)}
                </span>
              </div>
            </div>
            <p className="text-xs leading-none text-muted-foreground">
              {user.email}
            </p>
            <div className="flex items-center gap-1 text-xs">
              {user.is_verified ? (
                <>
                  <UserCheck className="h-3 w-3 text-green-600" />
                  <span className="text-green-600">Verified</span>
                </>
              ) : (
                <>
                  <UserCircle className="h-3 w-3 text-orange-600" />
                  <span className="text-orange-600">Unverified</span>
                </>
              )}
            </div>
          </div>
        </DropdownMenuLabel>
        
        <DropdownMenuSeparator />
        
        <DropdownMenuItem 
          onClick={() => router.push('/dashboard/profile')}
          className="cursor-pointer"
        >
          <User className="mr-2 h-4 w-4" />
          <span>Profile</span>
        </DropdownMenuItem>
        
        <DropdownMenuItem
          onClick={() => router.push('/dashboard/settings')}
          className="cursor-pointer"
        >
          <Settings className="mr-2 h-4 w-4" />
          <span>Settings</span>
        </DropdownMenuItem>

        <DropdownMenuSeparator />

        <DropdownMenuLabel>Theme</DropdownMenuLabel>

        <DropdownMenuItem
          onClick={() => setTheme('light')}
          className="cursor-pointer"
        >
          <Sun className="mr-2 h-4 w-4" />
          <span>Light</span>
        </DropdownMenuItem>

        <DropdownMenuItem
          onClick={() => setTheme('dark')}
          className="cursor-pointer"
        >
          <Moon className="mr-2 h-4 w-4" />
          <span>Dark</span>
        </DropdownMenuItem>

        <DropdownMenuSeparator />

        {user.role === 'doctor' && (
          <DropdownMenuItem 
            onClick={() => router.push('/doctor/dashboard')}
            className="cursor-pointer"
          >
            <Stethoscope className="mr-2 h-4 w-4" />
            <span>Doctor Portal</span>
          </DropdownMenuItem>
        )}

        {user.role === 'admin' && (
          <DropdownMenuItem 
            onClick={() => router.push('/admin/dashboard')}
            className="cursor-pointer"
          >
            <Shield className="mr-2 h-4 w-4" />
            <span>Admin Panel</span>
          </DropdownMenuItem>
        )}
        
        <DropdownMenuSeparator />
        
        <DropdownMenuItem 
          onClick={handleLogout}
          className="cursor-pointer text-red-600 focus:text-red-600"
          disabled={isLoggingOut}
        >
          <LogOut className="mr-2 h-4 w-4" />
          <span>{isLoggingOut ? 'Signing out...' : 'Sign out'}</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
