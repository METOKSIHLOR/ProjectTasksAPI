import axios from 'axios'
import {getConnectionId} from "./ws.js";

const api=axios.create({baseURL:'http://localhost:8000',withCredentials:true,headers:{'Content-Type':'application/json'}})
const r=p=>p.then(res=>res.data)

const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms))
const r_with_delay = async (p) => {
    const res = await p
    //console.log('запрос')
    await delay(200)
    return res.data
}
api.interceptors.request.use(
    config => {

        const connectionId = getConnectionId()

        if (connectionId) {
            config.headers['X-Connection-Id'] = connectionId
        }

        return config
    },
    error => Promise.reject(error)
)

// AUTH
export const registerUser=(name,email,password)=>r(api.post('/users/registration',{name,email,password}))
export const loginUser=(email,password)=>r(api.post('/users/auth/login',{email,password}))
export const logoutUser=()=>r(api.post('/users/auth/logout'))
export const getCurrentUser=()=>r(api.get('/users/me'))
export const updateCurrentUserName = name => r(api.patch('/users/me', { name }))

// USER SETTINGS
export const saveUserSettings = (settings) => r(api.put('/users/settings', settings));  // PUT запрос на сохранение настроек

// USER INVITES
export const getUserInvites = () => r(api.get('/users/invites'));
export const apiAcceptInvite = (inviteId) => r(api.delete(`/users/invites/${inviteId}`, {data:{status:"accepted"}}));
export const apiDeclineInvite = (inviteId) => r(api.delete(`/users/invites/${inviteId}`,{data:{status:"denied"}}));

// PROJECTS
export const createProject=data=>r(api.post('/projects',data))
export const getProjects=()=>r(api.get('/projects'))
export const getProject=id=>r(api.get(`/projects/${id}`))
export const deleteProject=id=>r(api.delete(`/projects/${id}`))
export const updateProject = (projectId, data) => r(api.patch(`/projects/${projectId}`, data))

// TASKS
export const getTasks = projectId => r(api.get(`/projects/${projectId}/tasks`))
export const getTask = (projectId, taskId) => r(api.get(`/projects/${projectId}/tasks/${taskId}`))
export const createTask = (projectId, data) => r(api.post(`/projects/${projectId}/tasks`, data))
export const deleteTask = (projectId, taskId) => r(api.delete(`/projects/${projectId}/tasks/${taskId}`))
export const updateTask = (projectId, taskId, data) => r(api.patch(`/projects/${projectId}/tasks/${taskId}`, data))

// PROJECT MEMBERS
export const createProjectMember=(projectId,email)=>r(api.post(`/projects/${projectId}/members`,{email}))
export const deleteProjectMember=(projectId,email)=>r(api.delete(`/projects/${projectId}/members`,{data:{email}}))

// COMMENTS
export const getComments=(projectId,taskId)=>r(api.get(`/projects/${projectId}/tasks/${taskId}/comments`))
export const createComment=(projectId,taskId,data)=>r(api.post(`/projects/${projectId}/tasks/${taskId}/comments`,data))
export const deleteComment=(projectId,taskId,commentId)=>r(api.delete(`/projects/${projectId}/tasks/${taskId}/comments/${commentId}`))