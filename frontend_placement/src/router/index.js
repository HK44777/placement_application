import { createRouter, createWebHistory } from 'vue-router'
import { authState } from '../store/auth'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import StudentRegister from '../views/StudentRegister.vue'
import CompanyRegister from '../views/CompanyRegister.vue'

import StudentLayout from '../views/student/StudentLayout.vue'
import StudentHome from '../views/student/StudentHome.vue'
import StudentProfile from '../views/student/StudentProfile.vue'
import StudentProfileEdit from '../views/student/StudentProfileEdit.vue'
import StudentJobDetail from '../views/student/StudentJobDetail.vue'
import StudentApplicationStatus from '../views/student/StudentApplicationStatus.vue'

import CompanyLayout from '../views/company/CompanyLayout.vue'
import CompanyDashboard from '../views/company/CompanyDashboard.vue'
import CompanyProfile from '../views/company/CompanyProfile.vue'
import CompanyProfileEdit from '../views/company/CompanyProfileEdit.vue'
import CompanyDriveCreate from '../views/company/CompanyDriveCreate.vue'
import CompanyDriveDetail from '../views/company/CompanyDriveDetail.vue'
import CompanyDriveEdit from '../views/company/CompanyDriveEdit.vue'

import AdminLayout from '../views/admin/AdminLayout.vue'
import AdminDashboard from '../views/admin/AdminDashboard.vue'
import AdminCompanies from '../views/admin/AdminCompanies.vue'
import AdminStudents from '../views/admin/AdminStudents.vue'
import AdminDrives from '../views/admin/AdminDrives.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/login', name: 'Login', component: Login },
  { path: '/student-register', name: 'StudentRegister', component: StudentRegister },
  { path: '/company-register', name: 'CompanyRegister', component: CompanyRegister },
  
  {
    path: '/student',
    component: StudentLayout,
    meta: { requiresAuth: true, role: 'student' },
    children: [
      { path: 'home', name: 'StudentHome', component: StudentHome },
      { path: 'profile', name: 'StudentProfile', component: StudentProfile },
      { path: 'profile/edit', name: 'StudentProfileEdit', component: StudentProfileEdit },
      { path: 'job/:id', name: 'StudentJobDetail', component: StudentJobDetail },
      { path: 'application/:id', name: 'StudentApplicationStatus', component: StudentApplicationStatus }
    ]
  },
  {
    path: '/company',
    component: CompanyLayout,
    meta: { requiresAuth: true, role: 'company' },
    children: [
      { path: 'dashboard', name: 'CompanyDashboard', component: CompanyDashboard },
      { path: 'profile', name: 'CompanyProfile', component: CompanyProfile },
      { path: 'profile/edit', name: 'CompanyProfileEdit', component: CompanyProfileEdit },
      { path: 'drives/create', name: 'CompanyDriveCreate', component: CompanyDriveCreate },
      { path: 'drives/:id', name: 'CompanyDriveDetail', component: CompanyDriveDetail },
      { path: 'drives/:id/edit', name: 'CompanyDriveEdit', component: CompanyDriveEdit }
    ]
  },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, role: 'admin' },
    children: [
      { path: 'dashboard', name: 'AdminDashboard', component: AdminDashboard },
      { path: 'companies', name: 'AdminCompanies', component: AdminCompanies },
      { path: 'students', name: 'AdminStudents', component: AdminStudents },
      { path: 'drives', name: 'AdminDrives', component: AdminDrives }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const publicPages = ['/', '/login', '/student-register', '/company-register']
  const isPublicPage = publicPages.includes(to.path)

  if (authState.isAuthenticated) {
    // Prevent logged-in users from accessing login/register/home pages
    if (isPublicPage) {
      if (authState.role === 'student') return next('/student/home')
      if (authState.role === 'company') return next('/company/dashboard')
      if (authState.role === 'admin') return next('/admin/dashboard')
    }
    
    // Prevent students from accessing company routes, etc.
    if (to.meta.role && authState.role !== to.meta.role) {
      return next('/')
    }
    
    next()
  } else {
    // Prevent logged-out users from accessing protected pages
    if (to.meta.requiresAuth) {
      return next('/login')
    }
    next()
  }
})

export default router
