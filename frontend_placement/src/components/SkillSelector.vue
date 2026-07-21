<template>
  <div class="skill-selector position-relative">
    <div class="form-control d-flex flex-wrap gap-2 align-items-center" @click="focusInput" style="min-height: 42px; cursor: text;">
      <span v-for="skill in selectedSkills" :key="skill" class="badge bg-secondary d-flex align-items-center gap-1">
        {{ skill }}
        <i class="bi bi-x-circle-fill" style="cursor: pointer;" @click.stop="removeSkill(skill)"></i>
      </span>
      <input 
        ref="searchInput"
        type="text" 
        class="border-0 flex-grow-1 shadow-none" 
        style="min-width: 100px; outline: none; background: transparent;"
        v-model="searchQuery"
        @focus="showDropdown = true"
        @blur="handleBlur"
        :placeholder="selectedSkills.length ? '' : 'Type to search skills...'"
      />
    </div>
    
    <ul v-if="showDropdown && filteredSkills.length" class="list-group position-absolute w-100 shadow mt-1" style="z-index: 1000; max-height: 200px; overflow-y: auto;">
      <li 
        v-for="skill in filteredSkills" 
        :key="skill" 
        class="list-group-item list-group-item-action"
        style="cursor: pointer;"
        @mousedown.prevent="addSkill(skill)"
      >
        {{ skill }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: String, // comma-separated string from parent
    default: ''
  }
})

const emit = defineEmits(['update:modelValue'])

const predefinedSkills = [
  "Python", "Java", "C++", "C#", "JavaScript", "TypeScript", "SQL", "NoSQL",
  "HTML", "CSS", "React", "Angular", "Vue.js", "Node.js", "Django", "Flask",
  "Spring Boot", "AWS", "Azure", "Google Cloud Platform (GCP)", "Docker",
  "Kubernetes", "Git", "CI/CD", "Machine Learning", "Deep Learning",
  "Data Analysis", "Pandas", "NumPy", "TensorFlow", "PyTorch",
  "Natural Language Processing", "Computer Vision", "REST APIs", "GraphQL",
  "Microservices", "Data Structures", "Algorithms", "System Design",
  "Cybersecurity", "Linux", "Bash Scripting", "PowerShell", "Ruby", "PHP",
  "Go", "Rust", "Swift", "Kotlin", "Mobile App Development", "iOS Development",
  "Android Development", "UI/UX Design", "Figma", "Database Management",
  "PostgreSQL", "MySQL", "MongoDB", "Redis", "Kafka", "RabbitMQ", "Terraform",
  "Ansible", "Prometheus", "Grafana", "Spark", "Hadoop", "Tableau",
  "Power BI", "Data Warehousing", "ETL", "Snowflake"
]

const searchQuery = ref('')
const showDropdown = ref(false)
const searchInput = ref(null)

const selectedSkills = computed(() => {
  if (!props.modelValue) return []
  return props.modelValue.split(',').map(s => s.trim()).filter(s => s)
})

const filteredSkills = computed(() => {
  const query = searchQuery.value.toLowerCase()
  return predefinedSkills.filter(skill => 
    skill.toLowerCase().includes(query) && !selectedSkills.value.includes(skill)
  )
})

const focusInput = () => {
  searchInput.value?.focus()
}

const addSkill = (skill) => {
  const current = [...selectedSkills.value]
  if (!current.includes(skill)) {
    current.push(skill)
    emit('update:modelValue', current.join(', '))
  }
  searchQuery.value = ''
  searchInput.value?.focus()
}

const removeSkill = (skill) => {
  const current = selectedSkills.value.filter(s => s !== skill)
  emit('update:modelValue', current.join(', '))
}

const handleBlur = () => {
  // Add slight delay to allow mousedown on dropdown item to fire before dropdown hides
  setTimeout(() => {
    showDropdown.value = false
    searchQuery.value = ''
  }, 150)
}
</script>

<style scoped>
.form-control:focus-within {
  border-color: #86b7fe;
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
}
</style>
