<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50 flex flex-col">
    <header class="py-5 px-6">
      <div class="max-w-3xl mx-auto flex items-center justify-between">
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center">
            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <span class="text-lg font-semibold text-slate-800 tracking-tight">冯三十资源库</span>
        </div>
        <div class="flex items-center gap-3">
          <template v-if="isLoggedIn">
            <div class="relative">
              <button @click="showUserMenu = !showUserMenu" class="flex items-center gap-2 px-3 py-1.5 text-sm text-slate-600 hover:text-slate-800 transition">
                <div class="w-6 h-6 rounded-full bg-blue-500 text-white flex items-center justify-center text-xs font-bold">{{ userInfo.username?.charAt(0).toUpperCase() }}</div>
                {{ userInfo.username }}
                <span v-if="unreadCount > 0" class="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white text-[10px] rounded-full flex items-center justify-center">{{ unreadCount > 9 ? '9+' : unreadCount }}</span>
              </button>
              <div v-if="showUserMenu" class="absolute right-0 top-full mt-1 bg-white border border-slate-200 rounded-lg shadow-lg py-1 z-50 min-w-[140px]">
                <button @click="openMyWishes" class="w-full text-left px-4 py-2 text-sm text-slate-600 hover:bg-slate-50">我的许愿</button>
                <button @click="openReplies" class="w-full text-left px-4 py-2 text-sm text-slate-600 hover:bg-slate-50 flex items-center gap-2">
                  许愿回复
                  <span v-if="unreadCount > 0" class="w-4 h-4 bg-red-500 text-white text-[10px] rounded-full flex items-center justify-center">{{ unreadCount }}</span>
                </button>
                <button @click="handleLogout" class="w-full text-left px-4 py-2 text-sm text-red-500 hover:bg-slate-50">退出登录</button>
              </div>
            </div>
          </template>
          <template v-else>
            <button @click="showLoginModal = true" class="px-3 py-1.5 text-sm text-slate-600 hover:text-slate-800 transition">登录</button>
            <button @click="showRegisterModal = true" class="px-3 py-1.5 text-sm text-white bg-slate-800 rounded-lg hover:bg-slate-700 transition">注册</button>
          </template>
        </div>
      </div>
    </header>

    <main class="flex-1 flex items-start justify-center pt-10 sm:pt-16 px-4">
      <div class="w-full max-w-2xl">
        <div class="text-center mb-8">
          <h1 class="text-4xl sm:text-5xl font-extralight text-slate-800 tracking-tight mb-3">发现网盘资源</h1>
          <p class="text-slate-400 text-base">搜索你需要的网盘分享链接</p>
        </div>

        <div class="relative group">
          <div class="absolute -inset-0.5 bg-gradient-to-r from-slate-200 to-blue-200 rounded-2xl blur opacity-0 group-hover:opacity-100 transition duration-300"></div>
          <div class="relative flex items-center bg-white border border-slate-200 rounded-2xl shadow-sm group-hover:shadow-md transition-shadow duration-300">
            <input
              v-model="keyword"
              @keyup.enter="handleSearch"
              type="text"
              placeholder="输入关键词搜索..."
              class="flex-1 px-6 py-4 text-base bg-transparent focus:outline-none text-slate-700 placeholder:text-slate-300"
            />
            <button
              @click="handleSearch"
              class="mr-2 px-6 py-2.5 bg-slate-800 text-white text-sm font-medium rounded-xl hover:bg-slate-700 active:scale-95 transition-all duration-150"
            >
              搜索
            </button>
          </div>
        </div>

        <div v-if="hotSearches.length" class="mt-6">
          <p class="text-xs text-slate-400 mb-2.5">热门搜索</p>
          <div class="flex flex-wrap gap-2">
            <button v-for="item in hotSearches" :key="item" @click="quickSearch(item)" class="px-3.5 py-1.5 text-sm text-slate-500 bg-white border border-slate-100 rounded-full hover:border-slate-300 hover:text-slate-700 hover:shadow-sm transition-all">{{ item }}</button>
          </div>
        </div>

        <div v-if="announcements.length" class="mt-6">
          <p class="text-xs text-slate-400 mb-2.5">公告</p>
          <div class="grid grid-cols-4 gap-2">
            <button v-for="(a, idx) in announcements" :key="a.id" @click="openAnnouncement(a)" class="px-3 py-2 text-xs text-slate-500 bg-white border border-slate-100 rounded-full hover:border-blue-300 hover:text-blue-500 hover:shadow-sm transition-all truncate flex items-center justify-center gap-1.5">
              <span class="text-sm shrink-0">{{ announcementIcons[idx % announcementIcons.length] }}</span>
              <span class="truncate">{{ a.title }}</span>
            </button>
          </div>
        </div>

        <div class="mt-6">
          <button @click="openDonation" class="w-full px-4 py-2.5 text-sm text-slate-500 bg-white border border-slate-100 rounded-xl hover:border-amber-300 hover:text-amber-600 hover:shadow-sm transition-all flex items-center justify-center gap-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" /></svg>
            打赏捐赠
          </button>
        </div>

        <div class="mt-6">
          <button @click="openWishModal" class="w-full px-4 py-2.5 text-sm text-white bg-gradient-to-r from-blue-500 to-indigo-500 rounded-xl hover:from-blue-600 hover:to-indigo-600 transition-all flex items-center justify-center gap-2 shadow-sm">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" /></svg>
            许愿池 — 许个愿吧
          </button>
        </div>

        <div class="mt-10 px-4">
          <p class="text-center text-xs text-slate-400 font-medium mb-2">免责声明&注意事项</p>
          <div class="text-xs text-slate-300 leading-relaxed space-y-1">
            <p>1.所有资源均免费分享，请注意不要被软件内部诱导付费、参与任何活动等。</p>
            <p>2.内容均来自网络，仅供学习和交流参考，不得将上述内容用于商业或者非法用途，否则，一切后果由用户自负。</p>
            <p>3.版权争议与本人无关。如有侵权请与我联系处理。敬请谅解！</p>
          </div>
        </div>
      </div>
    </main>

    <footer class="py-5 text-center text-xs text-slate-300">公众号：冯三十 | 关注我获取资源</footer>

    <!-- 登录弹窗 -->
    <Teleport to="body">
      <div v-if="showLoginModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="showLoginModal = false">
        <div class="bg-white rounded-2xl shadow-xl w-[360px] max-w-[90vw] p-6">
          <div class="flex items-center justify-between mb-5">
            <h3 class="text-lg font-semibold text-slate-800">登录</h3>
            <button @click="showLoginModal = false" class="text-slate-400 hover:text-slate-600 text-xl">&times;</button>
          </div>
          <div class="space-y-3">
            <input v-model="loginForm.username" type="text" placeholder="用户名" class="w-full px-4 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-300" />
            <input v-model="loginForm.password" type="password" placeholder="密码" class="w-full px-4 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-300" />
            <button @click="handleLogin" :disabled="loginLoading" class="w-full py-2.5 bg-slate-800 text-white text-sm font-medium rounded-xl hover:bg-slate-700 disabled:opacity-50 transition">{{ loginLoading ? '登录中...' : '登录' }}</button>
          </div>
          <p class="text-center text-xs text-slate-400 mt-4">没有账号？<button @click="showLoginModal = false; showRegisterModal = true" class="text-blue-500 hover:underline">去注册</button></p>
        </div>
      </div>
    </Teleport>

    <!-- 注册弹窗 -->
    <Teleport to="body">
      <div v-if="showRegisterModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="showRegisterModal = false">
        <div class="bg-white rounded-2xl shadow-xl w-[360px] max-w-[90vw] p-6">
          <div class="flex items-center justify-between mb-5">
            <h3 class="text-lg font-semibold text-slate-800">注册</h3>
            <button @click="showRegisterModal = false" class="text-slate-400 hover:text-slate-600 text-xl">&times;</button>
          </div>
          <div class="space-y-3">
            <input v-model="registerForm.username" type="text" placeholder="用户名" class="w-full px-4 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-300" />
            <input v-model="registerForm.email" type="email" placeholder="邮箱" class="w-full px-4 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-300" />
            <input v-model="registerForm.password" type="password" placeholder="密码" class="w-full px-4 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-300" />
            <button @click="handleRegister" :disabled="registerLoading" class="w-full py-2.5 bg-slate-800 text-white text-sm font-medium rounded-xl hover:bg-slate-700 disabled:opacity-50 transition">{{ registerLoading ? '注册中...' : '注册' }}</button>
          </div>
          <p class="text-center text-xs text-slate-400 mt-4">已有账号？<button @click="showRegisterModal = false; showLoginModal = true" class="text-blue-500 hover:underline">去登录</button></p>
        </div>
      </div>
    </Teleport>

    <!-- 公告详情弹窗 -->
    <Teleport to="body">
      <div v-if="showAnnouncementModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="showAnnouncementModal = false">
        <div class="bg-white rounded-2xl shadow-xl w-[520px] max-w-[90vw] max-h-[80vh] overflow-y-auto p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-slate-800">{{ currentAnnouncement.title }}</h3>
            <button @click="showAnnouncementModal = false" class="text-slate-400 hover:text-slate-600 text-xl">&times;</button>
          </div>
          <MdPreview :model-value="currentAnnouncement.content || ''" />
        </div>
      </div>
    </Teleport>

    <!-- 打赏捐赠弹窗 -->
    <Teleport to="body">
      <div v-if="showDonationModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="showDonationModal = false">
        <div class="bg-white rounded-2xl shadow-xl w-[520px] max-w-[90vw] max-h-[80vh] overflow-y-auto p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-slate-800">打赏捐赠</h3>
            <button @click="showDonationModal = false" class="text-slate-400 hover:text-slate-600 text-xl">&times;</button>
          </div>
          <MdPreview :model-value="donationContent || ''" />
        </div>
      </div>
    </Teleport>

    <!-- 许愿弹窗 -->
    <Teleport to="body">
      <div v-if="showWishModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="showWishModal = false">
        <div class="bg-white rounded-2xl shadow-xl w-[420px] max-w-[90vw] p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-slate-800">许个愿吧</h3>
            <button @click="showWishModal = false" class="text-slate-400 hover:text-slate-600 text-xl">&times;</button>
          </div>
          <template v-if="isLoggedIn">
            <textarea v-model="wishContent" rows="4" placeholder="描述你想要的资源..." class="w-full px-4 py-3 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-300 resize-none"></textarea>
            <button @click="submitWish" :disabled="wishLoading" class="w-full mt-3 py-2.5 bg-gradient-to-r from-blue-500 to-indigo-500 text-white text-sm font-medium rounded-xl hover:from-blue-600 hover:to-indigo-600 disabled:opacity-50 transition">{{ wishLoading ? '提交中...' : '提交许愿' }}</button>
          </template>
          <template v-else>
            <p class="text-sm text-slate-400 text-center py-6">请先 <button @click="showWishModal = false; showLoginModal = true" class="text-blue-500 hover:underline">登录</button> 后再许愿</p>
          </template>
        </div>
      </div>
    </Teleport>

    <!-- 我的许愿弹窗 -->
    <Teleport to="body">
      <div v-if="showMyWishes" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="showMyWishes = false">
        <div class="bg-white rounded-2xl shadow-xl w-[520px] max-w-[90vw] max-h-[80vh] overflow-y-auto p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-slate-800">我的许愿</h3>
            <button @click="showMyWishes = false" class="text-slate-400 hover:text-slate-600 text-xl">&times;</button>
          </div>
          <div v-if="myWishes.length" class="space-y-3">
            <div v-for="w in myWishes" :key="w.id" class="p-3 border border-slate-100 rounded-xl">
              <p class="text-sm text-slate-700">{{ w.content }}</p>
              <div class="flex items-center gap-2 mt-2">
                <span class="text-xs px-2 py-0.5 rounded-full" :class="w.is_resolved ? 'bg-green-50 text-green-600' : 'bg-amber-50 text-amber-600'">{{ w.is_resolved ? '已回应' : '等待中' }}</span>
                <span class="text-xs text-slate-300">{{ w.created_at?.substring(0, 10) }}</span>
              </div>
              <div v-if="w.replies && w.replies.length" class="mt-2 pl-3 border-l-2 border-blue-100">
                <div v-for="r in w.replies" :key="r.id" class="text-xs text-slate-500 py-1">
                  <p>{{ r.content }}</p>
                  <a v-if="r.resource_link" :href="r.resource_link" target="_blank" class="text-blue-500 hover:underline">{{ r.resource_title || r.resource_link }}</a>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-8 text-sm text-slate-400">暂无许愿</div>
        </div>
      </div>
    </Teleport>

    <!-- 许愿回复弹窗 -->
    <Teleport to="body">
      <div v-if="showReplies" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="showReplies = false">
        <div class="bg-white rounded-2xl shadow-xl w-[520px] max-w-[90vw] max-h-[80vh] overflow-y-auto p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-slate-800">许愿回复</h3>
            <button @click="showReplies = false" class="text-slate-400 hover:text-slate-600 text-xl">&times;</button>
          </div>
          <div v-if="myReplies.length" class="space-y-3">
            <div v-for="r in myReplies" :key="r.reply_id" class="p-3 border border-slate-100 rounded-xl">
              <p class="text-xs text-slate-400 mb-1">许愿: {{ r.wish_content }}</p>
              <p class="text-sm text-slate-700">{{ r.reply_content }}</p>
              <a v-if="r.resource_link" :href="r.resource_link" target="_blank" class="text-xs text-blue-500 hover:underline mt-1 inline-block">{{ r.resource_title || r.resource_link }}</a>
            </div>
          </div>
          <div v-else class="text-center py-8 text-sm text-slate-400">暂无回复</div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getHotSearches, getCategories, getAnnouncements, getDonation, register as apiRegister, login as apiLogin, getMe, createWish, getMyWishes, getMyReplies, getUnreadCount, markRepliesAsRead } from '../api'
import { MdPreview } from 'md-editor-v3'
import 'md-editor-v3/lib/preview.css'

const router = useRouter()
const keyword = ref('')
const selectedCategoryId = ref('')
const hotSearches = ref([])
const categories = ref([])
const announcements = ref([])
const donationContent = ref('')

const announcementIcons = ['📢', '🔔', '📣', '📰', '💡', '🎯', '📌', '✨']

const isLoggedIn = ref(false)
const userInfo = ref({})
const showUserMenu = ref(false)
const unreadCount = ref(0)

const showLoginModal = ref(false)
const showRegisterModal = ref(false)
const loginForm = ref({ username: '', password: '' })
const registerForm = ref({ username: '', email: '', password: '' })
const loginLoading = ref(false)
const registerLoading = ref(false)

const showAnnouncementModal = ref(false)
const currentAnnouncement = ref({})

const showDonationModal = ref(false)

const showWishModal = ref(false)
const wishContent = ref('')
const wishLoading = ref(false)

const showMyWishes = ref(false)
const myWishes = ref([])

const showReplies = ref(false)
const myReplies = ref([])

const checkLogin = async () => {
  const token = localStorage.getItem('user_token')
  if (!token) { isLoggedIn.value = false; return }
  try {
    const res = await getMe()
    userInfo.value = res.data
    isLoggedIn.value = true
    const countRes = await getUnreadCount().catch(() => ({ data: { count: 0 } }))
    unreadCount.value = countRes.data.count || 0
  } catch {
    localStorage.removeItem('user_token')
    isLoggedIn.value = false
  }
}

const handleLogin = async () => {
  if (!loginForm.value.username || !loginForm.value.password) return
  loginLoading.value = true
  try {
    const res = await apiLogin(loginForm.value)
    localStorage.setItem('user_token', res.data.access_token)
    showLoginModal.value = false
    loginForm.value = { username: '', password: '' }
    await checkLogin()
  } catch { alert('登录失败') }
  finally { loginLoading.value = false }
}

const handleRegister = async () => {
  if (!registerForm.value.username || !registerForm.value.email || !registerForm.value.password) return
  registerLoading.value = true
  try {
    await apiRegister(registerForm.value)
    showRegisterModal.value = false
    registerForm.value = { username: '', email: '', password: '' }
    alert('注册成功，请登录')
    showLoginModal.value = true
  } catch { alert('注册失败') }
  finally { registerLoading.value = false }
}

const handleLogout = () => {
  localStorage.removeItem('user_token')
  isLoggedIn.value = false
  userInfo.value = {}
  showUserMenu.value = false
}

const openAnnouncement = (a) => {
  currentAnnouncement.value = a
  showAnnouncementModal.value = true
}

const openDonation = async () => {
  try {
    const res = await getDonation()
    donationContent.value = res.data.content || '暂无打赏信息'
  } catch { donationContent.value = '暂无打赏信息' }
  showDonationModal.value = true
}

const openMyWishes = async () => {
  showUserMenu.value = false
  showMyWishes.value = true
  try {
    const res = await getMyWishes()
    myWishes.value = res.data || []
  } catch { myWishes.value = [] }
}

const openReplies = async () => {
  showUserMenu.value = false
  showReplies.value = true
  try {
    const res = await getMyReplies()
    myReplies.value = res.data || []
    await markRepliesAsRead().catch(() => {})
    unreadCount.value = 0
  } catch { myReplies.value = [] }
}

const openWishModal = () => {
  wishContent.value = ''
  showWishModal.value = true
}

const submitWish = async () => {
  if (!wishContent.value.trim()) return
  wishLoading.value = true
  try {
    await createWish({ content: wishContent.value })
    showWishModal.value = false
    wishContent.value = ''
    alert('许愿成功！')
  } catch { alert('许愿失败，请先登录') }
  finally { wishLoading.value = false }
}

onMounted(async () => {
  try {
    const [hotRes, catRes, annRes] = await Promise.all([
      getHotSearches().catch(() => ({ data: [] })),
      getCategories().catch(() => ({ data: [] })),
      getAnnouncements().catch(() => ({ data: [] })),
    ])
    hotSearches.value = hotRes.data || []
    categories.value = catRes.data || []
    announcements.value = annRes.data || []
  } catch {}
  checkLogin()
})

const handleSearch = () => {
  const query = { keyword: keyword.value.trim() || undefined }
  if (selectedCategoryId.value) query.category_id = selectedCategoryId.value
  if (keyword.value.trim() || selectedCategoryId.value) router.push({ name: 'Search', query })
}

const quickSearch = (word) => {
  keyword.value = word
  selectedCategoryId.value = ''
  handleSearch()
}
</script>
