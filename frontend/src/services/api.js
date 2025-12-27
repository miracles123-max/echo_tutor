import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api/v1'

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json'
    }
})

export default {
    // Upload file
    uploadFile(file) {
        const formData = new FormData()
        formData.append('file', file)
        return apiClient.post('/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        })
    },

    // Get current section
    getCurrentSection(fileId) {
        return apiClient.get(`/session/${fileId}/current`)
    },

    // Submit answer
    submitAnswer(fileId, questionId, answer) {
        return apiClient.post(`/session/${fileId}/answer`, {
            question_id: questionId,
            answer: answer
        })
    },

    // Move to next section
    nextSection(fileId) {
        return apiClient.post(`/session/${fileId}/next`)
    },

    // Get audio URL
    getAudioUrl(filename) {
        return `http://localhost:8000/audio/${filename}`
    }
}
