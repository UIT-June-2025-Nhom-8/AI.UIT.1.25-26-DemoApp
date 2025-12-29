import { motion } from 'framer-motion'
import { Mail, Users, Lightbulb, Target, Rocket, Database, Brain, BarChart3, Server, Github, ArrowLeft } from 'lucide-react'
import { ArchitectureDiagram } from '../components/about/ArchitectureDiagram'
import { Link } from 'react-router-dom'

interface TeamMember {
  name: string
  studentId: string
  email: string
  avatar: string
}

const teamMembers: TeamMember[] = [
  {
    name: 'Lã Xuân Hồng',
    studentId: '25410056',
    email: '25410056@ms.uit.edu.vn',
    avatar: 'H',
  },
  {
    name: 'Lê Quang Hoài Đức',
    studentId: '25410034',
    email: '25410034@ms.uit.edu.vn',
    avatar: 'Đ',
  },
  {
    name: 'Nguyễn Minh Trọng',
    studentId: '25410150',
    email: '25410150@ms.uit.edu.vn',
    avatar: 'T',
  },
  {
    name: 'Trần Thanh Long',
    studentId: '25410088',
    email: '25410088@ms.uit.edu.vn',
    avatar: 'L',
  },
  {
    name: 'Nguyễn Minh Nhật',
    studentId: '25410104',
    email: '25410104@ms.uit.edu.vn',
    avatar: 'N',
  },
]

const techStack = [
  'Python 3.8+',
  'scikit-learn',
  'XGBoost',
  'LightGBM',
  'Pandas & NumPy',
  'React & TypeScript',
  'TailwindCSS',
  'FastAPI',
]

const modules = [
  {
    icon: Database,
    title: 'Data Pipeline',
    description:
      'Xử lý dữ liệu thô, làm sạch outliers, imputation, và feature engineering với các kỹ thuật như target encoding và interaction features.',
    color: 'from-blue-500 to-cyan-500',
  },
  {
    icon: Brain,
    title: 'Model Training',
    description:
      'Huấn luyện nhiều mô hình (Random Forest, XGBoost, LightGBM) với hyperparameter tuning và cross-validation để chọn mô hình tối ưu.',
    color: 'from-purple-500 to-pink-500',
  },
  {
    icon: BarChart3,
    title: 'Evaluation',
    description:
      'Đánh giá chi tiết với các metrics (R², RMSE, MAE, MAPE), phân tích feature importance và SHAP values để giải thích mô hình.',
    color: 'from-orange-500 to-red-500',
  },
  {
    icon: Server,
    title: 'Model Serving',
    description:
      'API service cho inference với input validation, error handling, và confidence scoring để sử dụng trong production.',
    color: 'from-green-500 to-teal-500',
  },
]

const stats = [
  { label: 'R² Score Target', value: '0.80+' },
  { label: 'Core Modules', value: '5' },
  { label: 'ML Algorithms', value: '3' },
  { label: 'MAPE Target', value: '<15%' },
]

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
}

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: {
      type: 'spring' as const,
      stiffness: 100,
    },
  },
}

export function AboutPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Back to Home Button */}
      <div className="container mx-auto px-6 pt-8">
        <Link to="/predict">
          <motion.button
            whileHover={{ scale: 1.05, x: -5 }}
            whileTap={{ scale: 0.95 }}
            className="flex items-center gap-2 px-6 py-3 bg-white/10 backdrop-blur-lg rounded-full text-white font-medium border border-white/20 hover:bg-white/20 transition-all shadow-lg"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Quay về Trang chủ</span>
          </motion.button>
        </Link>
      </div>

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Animated Background */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -inset-[10px] opacity-50">
            {[...Array(20)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute h-2 w-2 bg-purple-500 rounded-full"
                initial={{
                  x: Math.random() * window.innerWidth,
                  y: Math.random() * window.innerHeight,
                }}
                animate={{
                  x: Math.random() * window.innerWidth,
                  y: Math.random() * window.innerHeight,
                }}
                transition={{
                  duration: Math.random() * 10 + 10,
                  repeat: Infinity,
                  repeatType: 'reverse',
                }}
              />
            ))}
          </div>
        </div>

        <div className="relative container mx-auto px-6 py-32">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 200, delay: 0.2 }}
              className="inline-block mb-6"
            >
              <div className="p-4 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full">
                <Lightbulb className="w-12 h-12 text-white" />
              </div>
            </motion.div>

            <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-white via-purple-200 to-pink-200 bg-clip-text text-transparent">
              Hệ Thống Dự Báo Giá Nhà
            </h1>
            <p className="text-2xl text-purple-200 mb-2">Vietnam Housing Price Prediction System</p>
            <p className="text-lg text-purple-300">Đồ Án Cuối Kỳ - CS106.TTNT</p>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1, duration: 2, repeat: Infinity, repeatType: 'reverse' }}
              className="mt-12"
            >
              <div className="flex justify-center">
                <motion.div
                  animate={{ y: [0, 10, 0] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                  className="text-white"
                >
                  <svg
                    className="w-6 h-6"
                    fill="none"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path d="M19 14l-7 7m0 0l-7-7m7 7V3"></path>
                  </svg>
                </motion.div>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Team Section */}
      <section className="py-20 relative">
        <div className="container mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <div className="flex items-center justify-center gap-3 mb-4">
              <Users className="w-8 h-8 text-purple-400" />
              <h2 className="text-5xl font-bold text-white">Đội Ngũ Phát Triển</h2>
            </div>
            <div className="h-1 w-24 bg-gradient-to-r from-purple-500 to-pink-500 mx-auto rounded-full"></div>
          </motion.div>

          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6"
          >
            {teamMembers.map((member) => (
              <motion.div key={member.studentId} variants={itemVariants}>
                <motion.div
                  whileHover={{ y: -10, scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-6 border border-purple-500/20 hover:border-purple-500/50 transition-all duration-300 shadow-xl hover:shadow-purple-500/20 cursor-pointer group"
                >
                  <motion.div
                    whileHover={{ rotate: 360 }}
                    transition={{ duration: 0.6 }}
                    className="w-24 h-24 mx-auto mb-4 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white text-3xl font-bold shadow-lg group-hover:shadow-purple-500/50"
                  >
                    {member.avatar}
                  </motion.div>
                  <h3 className="text-xl font-bold text-white mb-2 text-center">{member.name}</h3>
                  <p className="text-purple-300 text-sm text-center mb-2">MSSV: {member.studentId}</p>
                  <div className="flex items-center justify-center gap-2 text-purple-400 text-sm">
                    <Mail className="w-4 h-4" />
                    <p className="truncate">{member.email}</p>
                  </div>
                </motion.div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Project Overview */}
      <section className="py-20 relative">
        <div className="container mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <div className="flex items-center justify-center gap-3 mb-4">
              <Target className="w-8 h-8 text-purple-400" />
              <h2 className="text-5xl font-bold text-white">Tổng Quan Dự Án</h2>
            </div>
            <div className="h-1 w-24 bg-gradient-to-r from-purple-500 to-pink-500 mx-auto rounded-full"></div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="max-w-4xl mx-auto"
          >
            <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-lg rounded-3xl p-8 border border-purple-500/20 shadow-2xl">
              <h3 className="text-2xl font-bold text-purple-400 mb-4">Về Dự Án</h3>
              <p className="text-gray-300 leading-relaxed mb-4">
                Hệ thống Dự báo Giá Nhà là một dự án Machine Learning nhằm xây dựng mô hình dự đoán giá bất động sản tại Việt
                Nam. Sử dụng dữ liệu từ thị trường nhà đất năm 2024, hệ thống áp dụng các kỹ thuật tiên tiến trong xử lý dữ
                liệu, feature engineering và ensemble learning để đạt độ chính xác cao.
              </p>
              <p className="text-gray-300 leading-relaxed mb-6">
                Dự án được phát triển theo phương pháp Agile với 5 module chính, từ tiền xử lý dữ liệu đến triển khai mô hình,
                đảm bảo tính khoa học và khả năng mở rộng.
              </p>

              <h3 className="text-2xl font-bold text-purple-400 mb-4 mt-8">Công Nghệ Sử Dụng</h3>
              <div className="flex flex-wrap gap-3">
                {techStack.map((tech, index) => (
                  <motion.span
                    key={tech}
                    initial={{ opacity: 0, scale: 0 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: index * 0.1 }}
                    whileHover={{ scale: 1.1 }}
                    className="px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full text-white text-sm font-medium shadow-lg hover:shadow-purple-500/50 transition-all cursor-pointer"
                  >
                    {tech}
                  </motion.span>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Modules Section */}
      <section className="py-20 relative">
        <div className="container mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <div className="flex items-center justify-center gap-3 mb-4">
              <Rocket className="w-8 h-8 text-purple-400" />
              <h2 className="text-5xl font-bold text-white">Các Module Chính</h2>
            </div>
            <div className="h-1 w-24 bg-gradient-to-r from-purple-500 to-pink-500 mx-auto rounded-full"></div>
          </motion.div>

          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-6xl mx-auto"
          >
            {modules.map((module) => {
              const Icon = module.icon
              return (
                <motion.div key={module.title} variants={itemVariants}>
                  <motion.div
                    whileHover={{ y: -10 }}
                    className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-8 border border-purple-500/20 hover:border-purple-500/50 transition-all duration-300 shadow-xl hover:shadow-purple-500/20 h-full group"
                  >
                    <motion.div
                      whileHover={{ scale: 1.2, rotate: 360 }}
                      transition={{ duration: 0.6 }}
                      className={`w-16 h-16 rounded-xl bg-gradient-to-br ${module.color} flex items-center justify-center mb-6 shadow-lg`}
                    >
                      <Icon className="w-8 h-8 text-white" />
                    </motion.div>
                    <h4 className="text-2xl font-bold text-white mb-3 group-hover:text-purple-400 transition-colors">
                      {module.title}
                    </h4>
                    <p className="text-gray-400 leading-relaxed">{module.description}</p>
                  </motion.div>
                </motion.div>
              )
            })}
          </motion.div>
        </div>
      </section>

      {/* Architecture Design Section */}
      <section className="py-20 relative bg-gradient-to-b from-transparent via-purple-900/10 to-transparent">
        <div className="container mx-auto px-6">
          <ArchitectureDiagram />
        </div>
      </section>

      {/* Statistics */}
      <section className="py-20 relative">
        <div className="container mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-5xl font-bold text-white mb-4">Thống Kê Dự Án</h2>
            <div className="h-1 w-24 bg-gradient-to-r from-purple-500 to-pink-500 mx-auto rounded-full"></div>
          </motion.div>

          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-5xl mx-auto"
          >
            {stats.map((stat, index) => (
              <motion.div key={stat.label} variants={itemVariants}>
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/30 hover:border-purple-500 transition-all shadow-xl hover:shadow-purple-500/30"
                >
                  <motion.div
                    initial={{ scale: 0 }}
                    whileInView={{ scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: index * 0.1, type: 'spring', stiffness: 200 }}
                    className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent mb-2"
                  >
                    {stat.value}
                  </motion.div>
                  <p className="text-gray-400 text-sm">{stat.label}</p>
                </motion.div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-purple-500/20">
        <div className="container mx-auto px-6 text-center">
          <p className="text-gray-400 mb-2">Đồ Án Cuối Kỳ - CS106.TTNT</p>
          <p className="text-gray-500 mb-4">Trường Đại Học Công Nghệ Thông Tin - UIT</p>

          {/* GitHub Link */}
          <motion.a
            href="https://github.com/UIT-June-2025-Nhom-8/AI.UIT.1.25-26"
            target="_blank"
            rel="noopener noreferrer"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full text-white font-medium shadow-lg hover:shadow-purple-500/50 transition-all mb-4"
          >
            <Github className="w-5 h-5" />
            <span>View on GitHub</span>
          </motion.a>

          <p className="text-gray-600 text-sm mt-4">© 2025 - Vietnam Housing Price Prediction System</p>
        </div>
      </footer>
    </div>
  )
}
