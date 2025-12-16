<template>
  <div class="loading-spinner" :class="{ 'overlay': overlay }">
    <div class="spinner-container">
      <div class="spinner" :class="size">
        <div class="bounce1"></div>
        <div class="bounce2"></div>
        <div class="bounce3"></div>
      </div>
      <p v-if="message" class="loading-message">{{ message }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LoadingSpinner',
  props: {
    overlay: {
      type: Boolean,
      default: false
    },
    size: {
      type: String,
      default: 'medium',
      validator: (value) => ['small', 'medium', 'large'].includes(value)
    },
    message: {
      type: String,
      default: ''
    }
  }
}
</script>

<style scoped>
.loading-spinner {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
}

.loading-spinner.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(5px);
  z-index: 9999;
}

.spinner-container {
  text-align: center;
}

.spinner {
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
}

.spinner.small {
  width: 30px;
}

.spinner.medium {
  width: 50px;
}

.spinner.large {
  width: 70px;
}

.spinner > div {
  width: 18%;
  height: 18%;
  background-color: #667eea;
  border-radius: 100%;
  display: inline-block;
  animation: sk-bouncedelay 1.4s infinite ease-in-out both;
}

.spinner .bounce1 {
  animation-delay: -0.32s;
}

.spinner .bounce2 {
  animation-delay: -0.16s;
}

.loading-message {
  margin-top: 1rem;
  color: #667eea;
  font-weight: 500;
}

.overlay .loading-message {
  color: white;
}

@keyframes sk-bouncedelay {
  0%, 80%, 100% { 
    transform: scale(0);
  } 40% { 
    transform: scale(1.0);
  }
}
</style>