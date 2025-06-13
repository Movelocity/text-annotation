<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  House as HouseIcon,
  Edit as EditIcon,
  Collection as CollectionIcon,
  Setting as SettingIcon,
  Upload as UploadIcon,
  User as UserIcon,
  Bell as BellIcon,
  Search as SearchIcon
} from '@element-plus/icons-vue'

// Props
defineProps<{
  isHeaderVisible: boolean
}>()

// Current route for active navigation
const route = useRoute()
const currentPath = computed(() => route.path)
</script>

<template>
  <div>
    <!-- Mobile header -->
    <header class="mobile-header">
      <div class="mobile-header-content">
        <div class="mobile-logo">
          <img src="/favicon.ico" alt="Logo" class="logo-image" />
          <h2>文本数据标注</h2>
        </div>

        <nav class="mobile-nav">
          <ul class="mobile-menu">
            <li :class="{ active: currentPath === '/pages/home' }">
              <router-link to="/pages/home">
                <HouseIcon class="nav-icon" />
              </router-link>
            </li>
            <li :class="{ active: currentPath === '/pages/annotation' }">
              <router-link to="/pages/annotation">
                <EditIcon class="nav-icon" />
              </router-link>
            </li>
            <li :class="{ active: currentPath === '/pages/batch-annotation' }">
              <router-link to="/pages/batch-annotation">
                <CollectionIcon class="nav-icon" />
              </router-link>
            </li>
            <li :class="{ active: currentPath === '/pages/data-import' }">
              <router-link to="/pages/data-import">
                <UploadIcon class="nav-icon" />
              </router-link>
            </li>
            <li :class="{ active: currentPath === '/pages/label-manage' }">
              <router-link to="/pages/label-manage">
                <SettingIcon class="nav-icon" />
              </router-link>
            </li>
          </ul>
        </nav>
      </div>
    </header>

    <!-- Desktop header -->
    <header
      class="app-header header-visible"
    >
      <div class="header-content">
        <div class="header-left">
          <div class="logo-container">
            <img src="/favicon.ico" alt="Logo" class="logo-image" />
            <h2 class="logo-text">文本数据标注</h2>
          </div>

          <!-- Navigation menu -->
          <nav class="header-nav">
            <ul class="nav-menu">
              <li :class="{ active: currentPath === '/pages/home' }">
                <router-link to="/pages/home">
                  <HouseIcon class="nav-icon" />
                  <span>首页</span>
                </router-link>
              </li>
              <li :class="{ active: currentPath === '/pages/annotation' }">
                <router-link to="/pages/annotation">
                  <EditIcon class="nav-icon" />
                  <span>数据标注</span>
                </router-link>
              </li>
              <li :class="{ active: currentPath === '/pages/batch-annotation' }">
                <router-link to="/pages/batch-annotation">
                  <CollectionIcon class="nav-icon" />
                  <span>批量标注</span>
                </router-link>
              </li>
              <li :class="{ active: currentPath === '/pages/data-import' }">
                <router-link to="/pages/data-import">
                  <UploadIcon class="nav-icon" />
                  <span>数据导入</span>
                </router-link>
              </li>
              <li :class="{ active: currentPath === '/pages/label-manage' }">
                <router-link to="/pages/label-manage">
                  <SettingIcon class="nav-icon" />
                  <span>标签管理</span>
                </router-link>
              </li>
            </ul>
          </nav>
        </div>

        <div class="header-right">
          <div class="header-search">
            <div class="search-input-container">
              <SearchIcon class="search-icon" />
              <input 
                type="text" 
                placeholder="搜索数据..." 
                class="search-input"
              />
              <button class="search-clear-btn" aria-label="Clear search">×</button>
            </div>
          </div>

          <div class="header-actions">
            <div class="notification-badge">
              <button class="icon-button">
                <BellIcon class="action-icon" />
                <span class="badge">2</span>
              </button>
            </div>

            <div class="user-dropdown">
              <button class="icon-button user-dropdown-btn">
                <UserIcon class="action-icon" />
              </button>
              <div class="dropdown-menu">
                <a href="#" class="dropdown-item">个人设置</a>
                <a href="#" class="dropdown-item">系统设置</a>
                <div class="dropdown-divider"></div>
                <a href="#" class="dropdown-item">退出</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  </div>
</template>

<style scoped>
/* Logo styles */
.logo-container {
  height: 50px;
  display: flex;
  align-items: center;
  padding: 0 var(--spacing-md);
  overflow: hidden;
}

.logo-image {
  width: 32px;
  height: 32px;
  margin-right: var(--spacing-sm);
}

.logo-text {
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0;
  white-space: nowrap;
}

/* Header styles */
.app-header {
  height: 50px;
  background-color: var(--background-light);
  border-bottom: 1px solid var(--divider-color);
  padding: 0 var(--spacing-lg);
  position: sticky;
  top: 0;
  z-index: 100;
  transition: transform 0.3s ease;
}

.header-hidden {
  transform: translateY(-100%);
}

.header-visible {
  transform: translateY(0);
}

.header-content {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
}

/* Navigation styles */
.header-nav {
  min-width: 300px;
  margin-left: var(--spacing-lg);
}

.nav-menu {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  height: 50px;
}

.nav-menu li {
  height: 100%;
  position: relative;
}

.nav-menu li a {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 var(--spacing-lg);
  color: var(--text-primary);
  text-decoration: none;
}

.nav-menu li a:hover {
  color: var(--primary-color);
}

.nav-menu li.active a {
  color: var(--primary-color);
}

.nav-menu li.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: var(--primary-color);
}

.nav-icon {
  width: 20px;
  height: 20px;
  margin-right: var(--spacing-sm);
}

/* Search styles */
.header-search {
  width: 300px;
  margin-right: var(--spacing-lg);
}

.search-input-container {
  position: relative;
  display: flex;
  align-items: center;
  background-color: var(--background-dark);
  border-radius: var(--border-radius-md);
  padding: 0 var(--spacing-sm);
  height: 40px;
}

.search-icon {
  width: 18px;
  height: 18px;
  color: var(--text-secondary);
  margin: 0 var(--spacing-sm);
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  height: 100%;
  padding: 0 var(--spacing-sm);
  color: var(--text-primary);
  font-size: 0.9rem;
  outline: none;
}

.search-clear-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0 var(--spacing-sm);
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-clear-btn:hover {
  color: var(--text-primary);
}

/* Action buttons */
.header-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.icon-button {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--background-dark);
  border: none;
  cursor: pointer;
  position: relative;
  transition: background-color 0.2s ease;
}

.icon-button:hover {
  background-color: var(--divider-color);
}

.action-icon {
  width: 20px;
  height: 20px;
  color: var(--text-primary);
}

.notification-badge {
  position: relative;
}

.badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background-color: var(--error-color);
  color: white;
  font-size: 0.7rem;
  width: 12px;
  height: 18px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 var(--spacing-xs);
}

.user-dropdown {
  position: relative;
}

.user-dropdown-btn {
  background-color: var(--primary-light);
}

.user-dropdown-btn .action-icon {
  color: white;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background-color: var(--background-light);
  border-radius: var(--border-radius-md);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  min-width: 150px;
  padding: var(--spacing-xs) 0;
  z-index: 10;
  display: none;
  margin-top: 5px;
}

.dropdown-menu::before {
  content: '';
  position: absolute;
  top: -5px;
  left: 0;
  right: 0;
  height: 5px;
  background: transparent;
}

.user-dropdown:hover .dropdown-menu {
  display: block;
}

.dropdown-item {
  display: block;
  padding: var(--spacing-sm) var(--spacing-md);
  color: var(--text-primary);
  text-decoration: none;
  transition: background-color 0.2s ease;
}

.dropdown-item:hover {
  background-color: var(--background-dark);
}

.dropdown-divider {
  height: 1px;
  background-color: var(--divider-color);
  margin: var(--spacing-xs) 0;
}

/* Mobile styles */
.mobile-header {
  display: none;
  height: 50px;
  background-color: var(--background-light);
  border-bottom: 1px solid var(--divider-color);
  padding: 0 var(--spacing-md);
  position: sticky;
  top: 0;
  z-index: 100;
}

.mobile-header-content {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.mobile-logo {
  display: flex;
  align-items: center;
}

.mobile-logo h2 {
  margin: 0;
  font-size: 1.2rem;
  margin-left: var(--spacing-sm);
}

.mobile-nav {
  display: flex;
  align-items: center;
}

.mobile-menu {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
}

.mobile-menu li {
  margin: 0 var(--spacing-xs);
}

.mobile-menu li a {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: var(--border-radius-md);
  color: var(--text-primary);
  transition: background-color 0.2s ease;
}

.mobile-menu li a:hover {
  background-color: var(--background-dark);
}

.mobile-menu li.active a {
  color: var(--primary-color);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .mobile-header {
    display: block;
  }

  .app-header {
    display: none;
  }

  .header-search {
    width: 100%;
  }
}
</style>
