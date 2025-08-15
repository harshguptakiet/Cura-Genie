import { AppRouterInstance } from 'next/dist/shared/lib/app-router-context.shared-runtime'

export const navigationRoutes = {
  home: '/',
  landing: '/landing', 
  login: '/auth/login',
  register: '/auth/register',
  dashboard: '/dashboard',
  debugAuth: '/debug-auth'
} as const

export type NavigationRoute = keyof typeof navigationRoutes

export const navigateTo = (router: AppRouterInstance, route: NavigationRoute) => {
  router.push(navigationRoutes[route])
}

export const getRouteUrl = (route: NavigationRoute): string => {
  return navigationRoutes[route]
}
