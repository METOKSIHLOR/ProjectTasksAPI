import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import ProjectPage from '../views/ProjectPage.vue'
import ProjectNotFound from '../views/PageNotFound.vue'
import Register from '../views/Register.vue'
import Login from '../views/Login.vue'
import TaskPage from '../views/TaskPage.vue'
import { getCurrentUser } from '../api/api.js'
import {currentUser, setCurrentUser, setUnauthorized} from '../store/auth_store.js'
import Settings from "../views/Settings.vue";
import PasswordRecover from "../views/PasswordRecover.vue";

const routes = [
    { path: '/', name: 'dashboard', component: Dashboard },
    { path: '/projects', name: 'projects-empty', component: ProjectNotFound },
    { path: '/projects/:projectId', name: 'project', component: ProjectPage },
    { path: '/settings', name: 'settings', component: Settings },
    { path: '/login', name: 'login', component: Login },
    { path: '/register', name: 'register', component: Register },
    { path: '/password-recover', name: 'recover', component: PasswordRecover },
    { path: '/projects/:projectId/tasks/:taskId', name: 'task', component: TaskPage },
    { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

router.beforeEach(async (to, from, next) => {
    const publicPages = ['/login', '/register', '/password-recover']
    const authRequired = !publicPages.includes(to.path)

    // Если статус юзера ещё неизвестен, делаем запрос
    if (currentUser.value === null) {
        try {
            const user = await getCurrentUser()
            setCurrentUser(user)
        } catch {
            setUnauthorized()
            if (authRequired) return next('/login')
        }
    }

    // Если пользователь авторизован и идёт на публичную страницу
    if (currentUser.value && publicPages.includes(to.path)) {
        return next('/')
    }

    // Если не авторизован и страница защищённая
    if (currentUser.value === false && authRequired) {
        return next('/login')
    }

    next()
})

export default router