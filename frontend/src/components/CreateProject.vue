<template>
  <div>
    <!-- Add Project Button -->
    <button @click="openModal" class="add-project-btn">Add Project</button>

    <!-- Project Creation Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Create New Project</h2>
          <button @click="closeModal" class="close-btn">&times;</button>
        </div>

        <form @submit.prevent="createProject">
          <div class="form-group">
            <label for="project-name">Project Name</label>
            <input
              id="project-name"
              v-model="projectName"
              type="text"
              required
              placeholder="Enter project name"
            />
          </div>

          <div class="form-group">
            <label for="project-description">Description</label>
            <textarea
              id="project-description"
              v-model="projectDescription"
              rows="3"
              placeholder="Enter project description"
              required
            ></textarea>
          </div>

          <div class="form-actions">
            <button type="submit" :disabled="isSubmitting" class="submit-button">
              {{ isSubmitting ? 'Creating...' : 'Create Project' }}
            </button>
          </div>

          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>

          <div v-if="successMessage" class="success-message">
            {{ successMessage }}
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { API_BASE_URL } from '../utils/config'
import { fetchWithAuth } from '../utils/api'

const projectName = ref('')
const projectDescription = ref('')
const isSubmitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const showModal = ref(false)

const openModal = () => {
  showModal.value = true
  projectName.value = ''
  projectDescription.value = ''
  errorMessage.value = ''
  successMessage.value = ''
}

const closeModal = () => {
  showModal.value = false
}

const createProject = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  isSubmitting.value = true

  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/project`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: projectName.value,
        description: projectDescription.value,
      }),
    })

    if (response.ok) {
      const data = await response.json()
      successMessage.value = data.message || 'Project created successfully!'
      setTimeout(() => {
        closeModal()
      }, 1500)
    } else {
      const errorData = await response.json()
      errorMessage.value = errorData.error || 'Failed to create project. Please try again.'
    }
  } catch (error) {
    console.error('Error creating project:', error)
    errorMessage.value = 'An unexpected error occurred. Please try again.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.add-project-btn {
  padding: 10px 16px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.add-project-btn:hover {
  background-color: #45a049;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  width: 90%;
  max-width: 500px;
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.close-btn:hover {
  color: #333;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
}

input,
textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

textarea {
  resize: vertical;
}

.form-actions {
  margin-top: 20px;
}

.submit-button {
  width: 100%;
  padding: 10px 15px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.submit-button:hover {
  background-color: #45a049;
}

.submit-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error-message {
  margin-top: 15px;
  color: #d32f2f;
  font-size: 14px;
  text-align: center;
}

.success-message {
  margin-top: 15px;
  color: #388e3c;
  font-size: 14px;
  text-align: center;
}
</style>
