import axios from 'axios'

const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL || '/api/v1'

const api = axios.create({
    baseURL: API_BASE_URL,
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