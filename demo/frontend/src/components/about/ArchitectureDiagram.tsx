import { motion } from 'framer-motion'
import { Database, Brain, Server, Code, Layers, Zap, GitBranch, Package, Shield, Cpu } from 'lucide-react'
import { SystemOverview } from './SystemOverview'

interface ArchitectureNode {
  id: string
  title: string
  icon: any
  items: string[]
  color: string
  position: 'left' | 'center' | 'right'
}

const architectureNodes: ArchitectureNode[] = [
  {
    id: 'frontend',
    title: 'Frontend Layer',
    icon: Code,
    items: ['React + TypeScript', 'TailwindCSS', 'Framer Motion', 'React Router', 'Axios Client'],
    color: 'from-blue-500 to-cyan-500',
    position: 'left',
  },
  {
    id: 'api',
    title: 'API Gateway',
    icon: Server,
    items: ['FastAPI Framework', 'CORS Middleware', 'JWT Authentication', 'Request Validation', 'Error Handling'],
    color: 'from-green-500 to-teal-500',
    position: 'center',
  },
  {
    id: 'services',
    title: 'Business Logic',
    icon: Layers,
    items: [
      'Tree Model Service',
      'Tree Preprocess Service',
      'LLM Service (HuggingFace)',
      'Auth Service',
      'Helper Utilities',
    ],
    color: 'from-purple-500 to-pink-500',
    position: 'center',
  },
  {
    id: 'ml',
    title: 'ML Pipeline',
    icon: Brain,
    items: [
      'LightGBM Regressor',
      'XGBoost Regressor',
      'Ensemble Prediction',
      'Confidence Scoring',
      'Feature Engineering',
    ],
    color: 'from-orange-500 to-red-500',
    position: 'right',
  },
  {
    id: 'data',
    title: 'Data Processing',
    icon: Database,
    items: [
      'Label Encoding',
      'Location Stats',
      'Feature Extraction',
      'Data Validation',
      'Preprocessing Pipeline',
    ],
    color: 'from-indigo-500 to-purple-500',
    position: 'right',
  },
]

const techDetails = [
  {
    category: 'Frontend',
    icon: Code,
    color: 'from-blue-500 to-cyan-500',
    technologies: [
      { name: 'React 18', description: 'Modern UI framework with hooks' },
      { name: 'TypeScript', description: 'Type-safe development' },
      { name: 'TailwindCSS', description: 'Utility-first CSS framework' },
      { name: 'Framer Motion', description: 'Animation library' },
    ],
  },
  {
    category: 'Backend',
    icon: Server,
    color: 'from-green-500 to-teal-500',
    technologies: [
      { name: 'FastAPI', description: 'High-performance Python API' },
      { name: 'Pydantic', description: 'Data validation' },
      { name: 'JWT', description: 'Secure authentication' },
      { name: 'Uvicorn', description: 'ASGI web server' },
    ],
  },
  {
    category: 'Machine Learning',
    icon: Brain,
    color: 'from-purple-500 to-pink-500',
    technologies: [
      { name: 'LightGBM', description: 'Gradient boosting framework' },
      { name: 'XGBoost', description: 'Optimized distributed gradient boosting' },
      { name: 'HuggingFace', description: 'LLM for text parsing' },
      { name: 'Scikit-learn', description: 'ML utilities & metrics' },
    ],
  },
  {
    category: 'DevOps',
    icon: Package,
    color: 'from-orange-500 to-red-500',
    technologies: [
      { name: 'Docker', description: 'Containerization' },
      { name: 'GitHub Actions', description: 'CI/CD pipeline' },
      { name: 'Vite', description: 'Frontend build tool' },
      { name: 'Poetry/pip', description: 'Dependency management' },
    ],
  },
]

const dataFlow = [
  {
    step: 1,
    title: 'User Input',
    description: 'Người dùng nhập thông tin qua form hoặc text',
    icon: Code,
    color: 'blue',
  },
  {
    step: 2,
    title: 'API Request',
    description: 'Frontend gửi request đến FastAPI endpoint',
    icon: Zap,
    color: 'green',
  },
  {
    step: 3,
    title: 'Authentication',
    description: 'Xác thực JWT token và validate request',
    icon: Shield,
    color: 'yellow',
  },
  {
    step: 4,
    title: 'Text Parsing (Optional)',
    description: 'LLM service trích xuất features từ text',
    icon: Brain,
    color: 'purple',
  },
  {
    step: 5,
    title: 'Data Preprocessing',
    description: 'Label encoding, feature engineering',
    icon: Database,
    color: 'indigo',
  },
  {
    step: 6,
    title: 'Model Prediction',
    description: 'LightGBM/XGBoost hoặc ensemble prediction',
    icon: Cpu,
    color: 'pink',
  },
  {
    step: 7,
    title: 'Response',
    description: 'Trả về kết quả dự đoán với confidence score',
    icon: GitBranch,
    color: 'orange',
  },
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

export function ArchitectureDiagram() {
  return (
    <div className="space-y-20">
      {/* System Overview Section */}
      <SystemOverview />

      {/* Divider */}
      <div className="flex items-center justify-center">
        <div className="h-px w-full max-w-md bg-gradient-to-r from-transparent via-purple-500 to-transparent"></div>
      </div>

      {/* System Architecture Diagram */}
      <section>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h3 className="text-4xl font-bold text-white mb-3">System Architecture</h3>
          <p className="text-purple-300">Kiến trúc tổng thể của hệ thống</p>
        </motion.div>

        {/* Architecture Flow */}
        <div className="relative max-w-6xl mx-auto">
          {/* Connection Lines */}
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <svg className="w-full h-full" style={{ position: 'absolute' }}>
              <defs>
                <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#3b82f6" />
                  <stop offset="100%" stopColor="#8b5cf6" />
                </linearGradient>
              </defs>
              <motion.path
                d="M 150 200 Q 300 200 450 200"
                stroke="url(#gradient1)"
                strokeWidth="2"
                fill="none"
                initial={{ pathLength: 0 }}
                whileInView={{ pathLength: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 1.5, delay: 0.5 }}
              />
              <motion.path
                d="M 450 200 Q 600 200 750 200"
                stroke="url(#gradient1)"
                strokeWidth="2"
                fill="none"
                initial={{ pathLength: 0 }}
                whileInView={{ pathLength: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 1.5, delay: 0.7 }}
              />
            </svg>
          </div>

          {/* Architecture Nodes Grid */}
          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="grid grid-cols-1 md:grid-cols-3 gap-6 relative z-10"
          >
            {architectureNodes.map((node) => {
              const Icon = node.icon
              return (
                <motion.div key={node.id} variants={itemVariants}>
                  <motion.div
                    whileHover={{ y: -5, scale: 1.02 }}
                    className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-6 border border-purple-500/20 hover:border-purple-500/50 transition-all shadow-xl h-full"
                  >
                    <motion.div
                      whileHover={{ rotate: 360 }}
                      transition={{ duration: 0.6 }}
                      className={`w-14 h-14 rounded-xl bg-gradient-to-br ${node.color} flex items-center justify-center mb-4 shadow-lg`}
                    >
                      <Icon className="w-7 h-7 text-white" />
                    </motion.div>
                    <h4 className="text-xl font-bold text-white mb-3">{node.title}</h4>
                    <ul className="space-y-2">
                      {node.items.map((item, idx) => (
                        <motion.li
                          key={idx}
                          initial={{ opacity: 0, x: -10 }}
                          whileInView={{ opacity: 1, x: 0 }}
                          viewport={{ once: true }}
                          transition={{ delay: idx * 0.1 }}
                          className="text-gray-400 text-sm flex items-start"
                        >
                          <span className="text-purple-400 mr-2">•</span>
                          {item}
                        </motion.li>
                      ))}
                    </ul>
                  </motion.div>
                </motion.div>
              )
            })}
          </motion.div>
        </div>
      </section>

      {/* Data Flow */}
      <section>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h3 className="text-4xl font-bold text-white mb-3">Data Flow</h3>
          <p className="text-purple-300">Luồng xử lý dữ liệu từ input đến output</p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="max-w-4xl mx-auto"
        >
          <div className="relative">
            {/* Vertical Timeline Line */}
            <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gradient-to-b from-purple-500 via-pink-500 to-orange-500"></div>

            {/* Flow Steps */}
            <div className="space-y-8">
              {dataFlow.map((flow, index) => {
                const Icon = flow.icon
                const isEven = index % 2 === 0

                return (
                  <motion.div key={flow.step} variants={itemVariants} className="relative">
                    <div className="flex items-center gap-6">
                      {/* Timeline Node */}
                      <motion.div
                        whileHover={{ scale: 1.2 }}
                        className={`relative z-10 w-16 h-16 rounded-full bg-gradient-to-br from-${flow.color}-500 to-${flow.color}-600 flex items-center justify-center shadow-lg`}
                      >
                        <Icon className="w-8 h-8 text-white" />
                      </motion.div>

                      {/* Content Card */}
                      <motion.div
                        initial={{ opacity: 0, x: isEven ? -20 : 20 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: index * 0.15 }}
                        whileHover={{ x: 10 }}
                        className="flex-1 bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-5 border border-purple-500/20 hover:border-purple-500/50 transition-all shadow-lg"
                      >
                        <div className="flex items-center gap-3 mb-2">
                          <span className="text-2xl font-bold text-purple-400">#{flow.step}</span>
                          <h4 className="text-lg font-bold text-white">{flow.title}</h4>
                        </div>
                        <p className="text-gray-400 text-sm">{flow.description}</p>
                      </motion.div>
                    </div>
                  </motion.div>
                )
              })}
            </div>
          </div>
        </motion.div>
      </section>

      {/* Technology Stack Details */}
      <section>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h3 className="text-4xl font-bold text-white mb-3">Technology Stack</h3>
          <p className="text-purple-300">Chi tiết công nghệ sử dụng trong từng layer</p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-6xl mx-auto"
        >
          {techDetails.map((category) => {
            const Icon = category.icon
            return (
              <motion.div key={category.category} variants={itemVariants}>
                <motion.div
                  whileHover={{ y: -5 }}
                  className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-6 border border-purple-500/20 hover:border-purple-500/50 transition-all shadow-xl h-full"
                >
                  <div className="flex items-center gap-3 mb-5">
                    <motion.div
                      whileHover={{ rotate: 360 }}
                      transition={{ duration: 0.6 }}
                      className={`w-12 h-12 rounded-lg bg-gradient-to-br ${category.color} flex items-center justify-center shadow-lg`}
                    >
                      <Icon className="w-6 h-6 text-white" />
                    </motion.div>
                    <h4 className="text-2xl font-bold text-white">{category.category}</h4>
                  </div>

                  <div className="space-y-3">
                    {category.technologies.map((tech, idx) => (
                      <motion.div
                        key={tech.name}
                        initial={{ opacity: 0, x: -20 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: idx * 0.1 }}
                        whileHover={{ x: 5 }}
                        className="bg-slate-800/50 rounded-lg p-3 border border-purple-500/10 hover:border-purple-500/30 transition-all cursor-pointer"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-white">{tech.name}</span>
                          <span className="text-xs text-purple-400 bg-purple-500/10 px-2 py-1 rounded">
                            {category.category}
                          </span>
                        </div>
                        <p className="text-sm text-gray-400 mt-1">{tech.description}</p>
                      </motion.div>
                    ))}
                  </div>
                </motion.div>
              </motion.div>
            )
          })}
        </motion.div>
      </section>

      {/* API Endpoints */}
      <section>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h3 className="text-4xl font-bold text-white mb-3">API Endpoints</h3>
          <p className="text-purple-300">Các endpoint chính của hệ thống</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="max-w-4xl mx-auto bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-8 border border-purple-500/20 shadow-2xl"
        >
          <div className="space-y-4">
            {[
              { method: 'POST', path: '/api/v1/auth/login', desc: 'Đăng nhập và lấy JWT token' },
              { method: 'POST', path: '/api/v1/auth/logout', desc: 'Đăng xuất người dùng' },
              { method: 'GET', path: '/api/v1/auth/me', desc: 'Lấy thông tin user hiện tại' },
              { method: 'POST', path: '/api/v1/parse', desc: 'Parse text thành features bằng LLM' },
              { method: 'POST', path: '/api/v1/predict', desc: 'Dự đoán giá nhà từ features' },
              { method: 'POST', path: '/api/v1/parse-and-predict', desc: 'Parse text và dự đoán trong 1 call' },
              { method: 'GET', path: '/api/v1/models', desc: 'Lấy danh sách các models' },
              { method: 'GET', path: '/api/v1/models/{name}', desc: 'Lấy thông tin chi tiết model' },
              { method: 'GET', path: '/api/v1/health', desc: 'Health check endpoint' },
            ].map((endpoint, idx) => {
              const methodColor =
                endpoint.method === 'GET'
                  ? 'from-green-500 to-green-600'
                  : endpoint.method === 'POST'
                    ? 'from-blue-500 to-blue-600'
                    : 'from-orange-500 to-orange-600'

              return (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: idx * 0.05 }}
                  whileHover={{ x: 5 }}
                  className="flex items-center gap-4 bg-slate-800/50 rounded-lg p-4 border border-purple-500/10 hover:border-purple-500/30 transition-all cursor-pointer"
                >
                  <span
                    className={`px-3 py-1 rounded-lg bg-gradient-to-r ${methodColor} text-white text-xs font-bold min-w-[60px] text-center`}
                  >
                    {endpoint.method}
                  </span>
                  <code className="text-purple-300 font-mono text-sm flex-1">{endpoint.path}</code>
                  <span className="text-gray-400 text-sm">{endpoint.desc}</span>
                </motion.div>
              )
            })}
          </div>
        </motion.div>
      </section>

      {/* Deployment Architecture */}
      <section>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h3 className="text-4xl font-bold text-white mb-3">Deployment Architecture</h3>
          <p className="text-purple-300">Kiến trúc triển khai production</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="max-w-5xl mx-auto"
        >
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                title: 'Frontend',
                platform: 'Vercel / Netlify',
                icon: Code,
                color: 'from-blue-500 to-cyan-500',
                features: ['Static Site Generation', 'CDN Distribution', 'Auto SSL', 'GitHub Integration'],
              },
              {
                title: 'Backend API',
                platform: 'Railway / Render',
                icon: Server,
                color: 'from-green-500 to-teal-500',
                features: ['Docker Container', 'Auto Scaling', 'Health Checks', 'Environment Variables'],
              },
              {
                title: 'ML Models',
                platform: 'Embedded in Backend',
                icon: Brain,
                color: 'from-purple-500 to-pink-500',
                features: ['Pre-trained Models', 'Model Versioning', 'Fast Inference', 'Model Registry'],
              },
            ].map((deployment, idx) => {
              const Icon = deployment.icon
              return (
                <motion.div
                  key={deployment.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: idx * 0.15 }}
                  whileHover={{ y: -5 }}
                  className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-6 border border-purple-500/20 hover:border-purple-500/50 transition-all shadow-xl"
                >
                  <motion.div
                    whileHover={{ rotate: 360 }}
                    transition={{ duration: 0.6 }}
                    className={`w-14 h-14 rounded-xl bg-gradient-to-br ${deployment.color} flex items-center justify-center mb-4 shadow-lg`}
                  >
                    <Icon className="w-7 h-7 text-white" />
                  </motion.div>
                  <h4 className="text-xl font-bold text-white mb-2">{deployment.title}</h4>
                  <p className="text-purple-400 text-sm mb-4">{deployment.platform}</p>
                  <ul className="space-y-2">
                    {deployment.features.map((feature, fidx) => (
                      <li key={fidx} className="text-gray-400 text-sm flex items-start">
                        <span className="text-green-400 mr-2">✓</span>
                        {feature}
                      </li>
                    ))}
                  </ul>
                </motion.div>
              )
            })}
          </div>
        </motion.div>
      </section>
    </div>
  )
}
