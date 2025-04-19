<template>
  <div class="pl-4">
    <!-- Add Project Button -->
    <button @click="openModal" class="add-project-btn">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-5 w-5 mr-2"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M12 6v6m0 0v6m0-6h6m-6 0H6"
        />
      </svg>
      Projekt hinzufügen
    </button>

    <!-- Project Creation Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Neues Projekt erstellen</h2>
          <button @click="closeModal" class="close-btn">&times;</button>
        </div>

        <form @submit.prevent="createProject">
          <div class="form-group">
            <label for="project-name">Projektname</label>
            <input
              id="project-name"
              v-model="projectName"
              type="text"
              required
              placeholder="Projektnamen eingeben"
            />
          </div>

          <div class="form-group">
            <label for="project-description">Beschreibung</label>
            <textarea
              id="project-description"
              v-model="projectDescription"
              rows="3"
              placeholder="Projektbeschreibung eingeben"
              required
            ></textarea>
          </div>

          <div class="form-actions">
            <button type="submit" :disabled="isSubmitting" class="submit-button">
              {{ isSubmitting ? 'Wird erstellt...' : 'Projekt erstellen' }}
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

const emit = defineEmits(['project-created'])

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
      // Emit event that a new project was created
      emit('project-created')
      setTimeout(() => {
        closeModal()
      }, 100)
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
  background: linear-gradient(to bottom, #4caf50, #45a049);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
}

.add-project-btn:hover {
  background: linear-gradient(to bottom, #55c159, #4caf50);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.add-project-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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
  background: linear-gradient(to bottom, #4caf50, #45a049);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.3s;
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
}

.submit-button:hover {
  background: linear-gradient(to bottom, #55c159, #4caf50);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.submit-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.submit-button:disabled {
  background: #cccccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
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
