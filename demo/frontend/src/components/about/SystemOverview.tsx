import { motion } from 'framer-motion'
import { ArrowRight, CheckCircle2 } from 'lucide-react'

const systemLayers = [
  {
    layer: 'Client Layer',
    description: 'User Interface & Interaction',
    technologies: ['React', 'TypeScript', 'TailwindCSS'],
    color: 'from-blue-500 to-cyan-500',
    responsibilities: [
      'Render UI components',
      'Handle user input',
      'Communicate with API',
      'Display predictions',
    ],
  },
  {
    layer: 'API Gateway',
    description: 'Request Routing & Authentication',
    technologies: ['FastAPI', 'JWT', 'Pydantic'],
    color: 'from-green-500 to-teal-500',
    responsibilities: [
      'Route API requests',
      'Authenticate users',
      'Validate input data',
      'Handle errors',
    ],
  },
  {
    layer: 'Business Logic',
    description: 'Services & Processing',
    technologies: ['Python Services', 'HuggingFace'],
    color: 'from-purple-500 to-pink-500',
    responsibilities: [
      'Preprocess data',
      'Parse text (LLM)',
      'Coordinate services',
      'Business rules',
    ],
  },
  {
    layer: 'ML Engine',
    description: 'Model Inference & Prediction',
    technologies: ['LightGBM', 'XGBoost', 'Ensemble'],
    color: 'from-orange-500 to-red-500',
    responsibilities: [
      'Load trained models',
      'Make predictions',
      'Calculate confidence',
      'Ensemble averaging',
    ],
  },
]

const features = [
  {
    title: 'High Performance',
    description: 'API response time < 300ms với caching',
    metric: '~200ms',
  },
  {
    title: 'High Accuracy',
    description: 'R² score của model trên test set',
    metric: '0.82',
  },
  {
    title: 'Scalable',
    description: 'Horizontal scaling với Docker containers',
    metric: 'Auto',
  },
  {
    title: 'Secure',
    description: 'JWT authentication và input validation',
    metric: 'JWT',
  },
]

const dataFlowSteps = [
  { from: 'User Input', to: 'Frontend Validation', time: '<10ms' },
  { from: 'Frontend', to: 'API Gateway', time: '<50ms' },
  { from: 'API Gateway', to: 'Auth Service', time: '<20ms' },
  { from: 'Auth Service', to: 'Business Logic', time: '<10ms' },
  { from: 'Business Logic', to: 'Preprocessing', time: '<30ms' },
  { from: 'Preprocessing', to: 'ML Model', time: '<50ms' },
  { from: 'ML Model', to: 'Response', time: '<30ms' },
  { from: 'Response', to: 'Display Result', time: '<20ms' },
]

export function SystemOverview() {
  return (
    <div className="space-y-16">
      {/* 3-Tier Architecture Overview */}
      <section>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h3 className="text-4xl font-bold text-white mb-3">3-Tier Architecture</h3>
          <p className="text-purple-300">Kiến trúc phân lớp rõ ràng và dễ mở rộng</p>
        </motion.div>

        <div className="relative max-w-6xl mx-auto">
          {/* Architecture Layers */}
          <div className="grid grid-cols-1 gap-8">
            {systemLayers.map((layer, index) => (
              <div key={layer.layer} className="relative">
                <motion.div
                  initial={{ opacity: 0, x: -50 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.15 }}
                  className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-6 border border-purple-500/20 shadow-xl"
                >
                  <div className="flex flex-col md:flex-row gap-6">
                    {/* Layer Info */}
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <div
                          className={`w-12 h-12 rounded-lg bg-gradient-to-br ${layer.color} flex items-center justify-center text-white font-bold text-lg`}
                        >
                          {index + 1}
                        </div>
                        <div>
                          <h4 className="text-xl font-bold text-white">{layer.layer}</h4>
                          <p className="text-sm text-purple-300">{layer.description}</p>
                        </div>
                      </div>

                      {/* Technologies */}
                      <div className="flex flex-wrap gap-2 mb-3">
                        {layer.technologies.map((tech) => (
                          <span
                            key={tech}
                            className={`px-3 py-1 rounded-full bg-gradient-to-r ${layer.color} text-white text-xs font-medium`}
                          >
                            {tech}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Responsibilities */}
                    <div className="flex-1">
                      <p className="text-sm font-semibold text-gray-400 mb-2">Responsibilities:</p>
                      <ul className="space-y-1">
                        {layer.responsibilities.map((resp, idx) => (
                          <li key={idx} className="text-sm text-gray-300 flex items-start">
                            <CheckCircle2 className="w-4 h-4 text-green-400 mr-2 mt-0.5 flex-shrink-0" />
                            {resp}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </motion.div>

                {/* Arrow between layers */}
                {index < systemLayers.length - 1 && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: index * 0.15 + 0.1 }}
                    className="flex justify-center py-3"
                  >
                    <ArrowRight className="w-8 h-8 text-purple-400 rotate-90" />
                  </motion.div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Data Flow Timeline */}
      <section>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h3 className="text-4xl font-bold text-white mb-3">Request Flow Timeline</h3>
          <p className="text-purple-300">Thời gian xử lý từng bước trong 1 prediction request</p>
        </motion.div>

        <div className="max-w-5xl mx-auto">
          <div className="relative bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-lg rounded-2xl p-8 border border-purple-500/20">
            {/* Timeline */}
            <div className="space-y-4">
              {dataFlowSteps.map((step, index) => {
                const totalTime = dataFlowSteps.slice(0, index + 1).reduce((sum, s) => {
                  return sum + parseInt(s.time.replace(/[<>ms]/g, ''))
                }, 0)

                return (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: index * 0.05 }}
                    className="flex items-center gap-4"
                  >
                    {/* Timeline dot */}
                    <div className="flex items-center gap-3 min-w-[250px]">
                      <div className="w-3 h-3 rounded-full bg-gradient-to-r from-purple-500 to-pink-500"></div>
                      <span className="text-white font-medium text-sm">{step.from}</span>
                    </div>

                    {/* Arrow */}
                    <ArrowRight className="w-5 h-5 text-purple-400 flex-shrink-0" />

                    {/* Destination */}
                    <div className="flex items-center gap-3 min-w-[250px]">
                      <span className="text-gray-300 text-sm">{step.to}</span>
                    </div>

                    {/* Time */}
                    <div className="ml-auto flex items-center gap-2">
                      <span className="text-xs text-purple-400 bg-purple-500/10 px-3 py-1 rounded-full font-mono">
                        {step.time}
                      </span>
                      <span className="text-xs text-gray-500 font-mono">Σ {totalTime}ms</span>
                    </div>
                  </motion.div>
                )
              })}

              {/* Total Time */}
              <div className="pt-4 border-t border-purple-500/20 mt-4">
                <div className="flex items-center justify-between">
                  <span className="text-white font-bold">Total Request Time:</span>
                  <span className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                    ~220ms
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* System Features Grid */}
      <section>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h3 className="text-4xl font-bold text-white mb-3">System Features</h3>
          <p className="text-purple-300">Các tính năng nổi bật của hệ thống</p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ y: -5, scale: 1.02 }}
              className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-6 border border-purple-500/20 hover:border-purple-500/50 transition-all shadow-xl text-center"
            >
              <div className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
                {feature.metric}
              </div>
              <h4 className="text-lg font-bold text-white mb-2">{feature.title}</h4>
              <p className="text-sm text-gray-400">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Tech Stack Summary */}
      <section>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h3 className="text-4xl font-bold text-white mb-3">Full Stack Overview</h3>
          <p className="text-purple-300">Công nghệ được sử dụng trong toàn bộ hệ thống</p>
        </motion.div>

        <div className="max-w-5xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              whileHover={{ y: -5 }}
              className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-6 border border-purple-500/20 hover:border-blue-500/50 transition-all shadow-xl"
            >
              <div className="text-center mb-4">
                <div className="w-16 h-16 mx-auto rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center mb-3">
                  <span className="text-2xl font-bold text-white">FE</span>
                </div>
                <h4 className="text-xl font-bold text-white">Frontend</h4>
              </div>
              <ul className="space-y-2 text-sm">
                <li className="text-gray-300">✓ React 18 + TypeScript</li>
                <li className="text-gray-300">✓ Vite Build Tool</li>
                <li className="text-gray-300">✓ TailwindCSS</li>
                <li className="text-gray-300">✓ Framer Motion</li>
                <li className="text-gray-300">✓ React Router</li>
              </ul>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
              whileHover={{ y: -5 }}
              className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-6 border border-purple-500/20 hover:border-green-500/50 transition-all shadow-xl"
            >
              <div className="text-center mb-4">
                <div className="w-16 h-16 mx-auto rounded-xl bg-gradient-to-br from-green-500 to-teal-500 flex items-center justify-center mb-3">
                  <span className="text-2xl font-bold text-white">BE</span>
                </div>
                <h4 className="text-xl font-bold text-white">Backend</h4>
              </div>
              <ul className="space-y-2 text-sm">
                <li className="text-gray-300">✓ Python 3.8+</li>
                <li className="text-gray-300">✓ FastAPI Framework</li>
                <li className="text-gray-300">✓ Pydantic Validation</li>
                <li className="text-gray-300">✓ JWT Auth</li>
                <li className="text-gray-300">✓ Uvicorn Server</li>
              </ul>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              whileHover={{ y: -5 }}
              className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-6 border border-purple-500/20 hover:border-purple-500/50 transition-all shadow-xl"
            >
              <div className="text-center mb-4">
                <div className="w-16 h-16 mx-auto rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center mb-3">
                  <span className="text-2xl font-bold text-white">ML</span>
                </div>
                <h4 className="text-xl font-bold text-white">Machine Learning</h4>
              </div>
              <ul className="space-y-2 text-sm">
                <li className="text-gray-300">✓ LightGBM</li>
                <li className="text-gray-300">✓ XGBoost</li>
                <li className="text-gray-300">✓ HuggingFace LLM</li>
                <li className="text-gray-300">✓ Scikit-learn</li>
                <li className="text-gray-300">✓ Pandas & NumPy</li>
              </ul>
            </motion.div>
          </div>
        </div>
      </section>
    </div>
  )
}
