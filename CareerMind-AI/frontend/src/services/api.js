import axios from 'axios'

const api = axios.create({
    baseURL: '/api/v1',
    timeout: 30000,
    headers: {
        Accept: 'application/json',
    },
})

api.interceptors.response.use(
    (response) => response,
    (error) => {
        error.userMessage =
            error.response?.data?.detail ||
            error.message ||
            'Something went wrong. Please try again.'

        return Promise.reject(error)
    }
)

export default api