import { useState } from 'react'
import { Play, BookOpen, Clock, ThumbsUp, Upload, Plus, Video, Image, FileText, X } from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/services/api'
import toast from 'react-hot-toast'

const VIDEOS = [
  { emoji:'🧬', bg:'#E8F4EC', title:'Understanding Insulin Resistance in PCOS', dur:12, cat:'Science',   likes:1240 },
  { emoji:'🌙', bg:'#F0E8F2', title:'Cycle Syncing: Eat & Move With Your Hormones', dur:18, cat:'Lifestyle', likes:2100 },
  { emoji:'🧘', bg:'#FDE8EC', title:'Stress & Cortisol: The PCOS Connection',   dur:9,  cat:'Mindset',   likes:980  },
  { emoji:'💊', bg:'#FEF0E8', title:'Top Supplements for PCOS — Evidence-Based', dur:14, cat:'Nutrition',  likes:1780 },
]

const ARTICLES = [
  { emoji:'🩺', bg:'#E8F4EC', title:'Talking to Your Doctor About PCOS',         sub:'Advocacy + questions to ask',   readMin:5  },
  { emoji:'😴', bg:'#F0E8F2', title:'Sleep Protocol for Hormonal Balance',        sub:'8-step bedtime routine',        readMin:4  },
  { emoji:'🥚', bg:'#FEF0E8', title:'PCOS and Fertility: What You Need to Know',  sub:'Planning, hope and next steps', readMin:8  },
  { emoji:'🏃', bg:'#FDE8EC', title:'Best Exercises for PCOS Bodies',             sub:'Low-impact and hormone-friendly',readMin:6  },
  { emoji:'🧠', bg:'#E8F4EC', title:'Managing PCOS Anxiety Naturally',            sub:'Proven coping strategies',      readMin:7  },
  { emoji:'🌿', bg:'#F0E8F2', title:'Anti-inflammatory Eating for PCOS',          sub:'Complete beginners guide',      readMin:10 },
]

interface UserContent {
  id: string
  title: string
  content_type: string
  description?: string
  content_url?: string
  content_text?: string
  thumbnail_url?: string
  tags: string[]
  view_count: number
  like_count: number
  created_at: string
}

export default function LearnPage() {
  const [tab, setTab] = useState('videos')
  const [playing, setPlaying] = useState(-1)
  const [showUpload, setShowUpload] = useState(false)
  const [uploadType, setUploadType] = useState<'video' | 'photo' | 'article'>('article')
  const [uploadForm, setUploadForm] = useState({
    title: '',
    description: '',
    content_text: '',
    tags: '',
  })
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const queryClient = useQueryClient()

  const { data: userContent = [] } = useQuery({
    queryKey: ['user-content'],
    queryFn: () => api.get('/user-content/').then(r => r.data),
  })

  const uploadMutation = useMutation({
    mutationFn: async (formData: FormData) => {
      return api.post('/user-content/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-content'] })
      setShowUpload(false)
      setUploadForm({ title: '', description: '', content_text: '', tags: '' })
      setSelectedFile(null)
      toast.success('Content uploaded successfully!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Upload failed')
    },
  })

  const handleUpload = () => {
    if (!uploadForm.title.trim()) {
      toast.error('Title is required')
      return
    }

    if (uploadType === 'article' && !uploadForm.content_text.trim()) {
      toast.error('Content text is required for articles')
      return
    }

    if ((uploadType === 'video' || uploadType === 'photo') && !selectedFile) {
      toast.error('File is required')
      return
    }

    const formData = new FormData()
    formData.append('title', uploadForm.title)
    formData.append('content_type', uploadType)
    formData.append('description', uploadForm.description)
    if (uploadForm.content_text) formData.append('content_text', uploadForm.content_text)
    if (uploadForm.tags) formData.append('tags', JSON.stringify(uploadForm.tags.split(',').map(t => t.trim())))
    if (selectedFile) formData.append('file', selectedFile)

    uploadMutation.mutate(formData)
  }

  return (
    <div className="pb-6">
      <div className="bg-gradient-to-br from-violet-600 to-indigo-800 text-white px-6 pt-14 pb-6">
        <h1 className="font-serif text-3xl italic mb-1">Learn</h1>
        <p className="text-sm opacity-80">Evidence-based PCOS education</p>
      </div>

      <div className="flex gap-3 px-5 py-4">
        {[
          { key: 'videos', label: 'Videos' },
          { key: 'articles', label: 'Articles' },
          { key: 'my-content', label: 'My Content' },
        ].map(t => (
          <button key={t.key} onClick={() => setTab(t.key)}
            className={"flex-1 py-2.5 rounded-2xl text-sm font-bold capitalize transition-all border " +
              (tab === t.key ? 'bg-violet-600 text-white border-violet-600' : 'bg-white text-gray-500 border-plum/10')}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Upload Button */}
      {tab === 'my-content' && (
        <div className="px-5 mb-4">
          <button
            onClick={() => setShowUpload(true)}
            className="w-full bg-violet-600 text-white py-3 rounded-2xl font-bold flex items-center justify-center gap-2"
          >
            <Plus size={20} />
            Add New Content
          </button>
        </div>
      )}

      {/* Upload Modal */}
      {showUpload && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl w-full max-w-md max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold">Add Content</h2>
                <button onClick={() => setShowUpload(false)} className="p-2">
                  <X size={24} />
                </button>
              </div>

              {/* Content Type Selection */}
              <div className="flex gap-2 mb-6">
                {[
                  { type: 'article', icon: FileText, label: 'Article' },
                  { type: 'photo', icon: Image, label: 'Photo' },
                  { type: 'video', icon: Video, label: 'Video' },
                ].map(({ type, icon: Icon, label }) => (
                  <button
                    key={type}
                    onClick={() => setUploadType(type as any)}
                    className={`flex-1 py-3 rounded-xl border-2 flex flex-col items-center gap-2 transition-all ${
                      uploadType === type ? 'border-violet-600 bg-violet-50' : 'border-gray-200'
                    }`}
                  >
                    <Icon size={24} className={uploadType === type ? 'text-violet-600' : 'text-gray-400'} />
                    <span className={`text-sm font-bold ${uploadType === type ? 'text-violet-600' : 'text-gray-500'}`}>
                      {label}
                    </span>
                  </button>
                ))}
              </div>

              {/* Form */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-bold text-gray-700 mb-1">Title *</label>
                  <input
                    type="text"
                    value={uploadForm.title}
                    onChange={(e) => setUploadForm(f => ({ ...f, title: e.target.value }))}
                    className="w-full p-3 border border-gray-200 rounded-xl"
                    placeholder="Enter title..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-bold text-gray-700 mb-1">Description</label>
                  <textarea
                    value={uploadForm.description}
                    onChange={(e) => setUploadForm(f => ({ ...f, description: e.target.value }))}
                    className="w-full p-3 border border-gray-200 rounded-xl h-20 resize-none"
                    placeholder="Optional description..."
                  />
                </div>

                {uploadType === 'article' && (
                  <div>
                    <label className="block text-sm font-bold text-gray-700 mb-1">Content *</label>
                    <textarea
                      value={uploadForm.content_text}
                      onChange={(e) => setUploadForm(f => ({ ...f, content_text: e.target.value }))}
                      className="w-full p-3 border border-gray-200 rounded-xl h-32 resize-none"
                      placeholder="Write your article content..."
                    />
                  </div>
                )}

                {(uploadType === 'video' || uploadType === 'photo') && (
                  <div>
                    <label className="block text-sm font-bold text-gray-700 mb-1">
                      {uploadType === 'video' ? 'Video File *' : 'Photo File *'}
                    </label>
                    <input
                      type="file"
                      accept={uploadType === 'video' ? 'video/*' : 'image/*'}
                      onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                      className="w-full p-3 border border-gray-200 rounded-xl"
                    />
                    {selectedFile && (
                      <p className="text-sm text-gray-500 mt-1">{selectedFile.name}</p>
                    )}
                  </div>
                )}

                <div>
                  <label className="block text-sm font-bold text-gray-700 mb-1">Tags</label>
                  <input
                    type="text"
                    value={uploadForm.tags}
                    onChange={(e) => setUploadForm(f => ({ ...f, tags: e.target.value }))}
                    className="w-full p-3 border border-gray-200 rounded-xl"
                    placeholder="Comma-separated tags..."
                  />
                </div>

                <button
                  onClick={handleUpload}
                  disabled={uploadMutation.isPending}
                  className="w-full bg-violet-600 text-white py-3 rounded-xl font-bold disabled:opacity-50"
                >
                  {uploadMutation.isPending ? 'Uploading...' : 'Upload Content'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="px-5 space-y-4">
        {tab === 'videos' && VIDEOS.map((v, i) => (
          <div key={i} className="card overflow-hidden">
            <div className="h-28 flex items-center justify-center relative cursor-pointer"
              style={{ background: v.bg }} onClick={() => setPlaying(playing === i ? -1 : i)}>
              <span className="text-5xl">{v.emoji}</span>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-12 h-12 rounded-full bg-white/90 shadow-lg flex items-center justify-center">
                  <Play size={20} className="text-violet-600 ml-0.5" fill="currentColor" />
                </div>
              </div>
              <span className="absolute top-2 right-2 bg-black/60 text-white text-xs px-2 py-0.5 rounded-full">
                {v.dur} min
              </span>
            </div>
            {playing === i && (
              <div className="bg-gray-900 h-40 flex items-center justify-center">
                <p className="text-white/60 text-sm">Video Player — connect your video source</p>
              </div>
            )}
            <div className="p-4">
              <p className="font-bold text-sm text-gray-800 mb-2 leading-snug">{v.title}</p>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="tag-sage">{v.cat}</span>
                  <span className="flex items-center gap-1 text-xs text-gray-400">
                    <Clock size={11} /> {v.dur} min
                  </span>
                </div>
                <span className="flex items-center gap-1 text-xs text-gray-400">
                  <ThumbsUp size={11} /> {v.likes.toLocaleString()}
                </span>
              </div>
            </div>
          </div>
        ))}

        {tab === 'articles' && ARTICLES.map((a, i) => (
          <div key={i} className="card flex gap-4 p-4 items-start">
            <div className="w-14 h-14 rounded-2xl flex items-center justify-center text-2xl flex-shrink-0"
              style={{ background: a.bg }}>{a.emoji}</div>
            <div className="flex-1 min-w-0">
              <p className="font-bold text-sm text-gray-800 leading-snug mb-1">{a.title}</p>
              <p className="text-xs text-gray-400 mb-2">{a.sub}</p>
              <span className="flex items-center gap-1 text-xs text-gray-400">
                <BookOpen size={10} /> {a.readMin} min read
              </span>
            </div>
            <button className="text-violet-500 font-bold text-xs flex-shrink-0 mt-1">Read</button>
          </div>
        ))}

        {tab === 'my-content' && (
          <>
            {userContent.length === 0 ? (
              <div className="text-center py-12">
                <Upload size={48} className="text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 mb-4">No content uploaded yet</p>
                <button
                  onClick={() => setShowUpload(true)}
                  className="bg-violet-600 text-white px-6 py-2 rounded-xl font-bold"
                >
                  Upload Your First Content
                </button>
              </div>
            ) : (
              userContent.map((content: UserContent) => (
                <div key={content.id} className="card p-4">
                  <div className="flex items-start gap-3">
                    <div className="w-12 h-12 rounded-xl bg-violet-100 flex items-center justify-center flex-shrink-0">
                      {content.content_type === 'video' && <Video size={20} className="text-violet-600" />}
                      {content.content_type === 'photo' && <Image size={20} className="text-violet-600" />}
                      {content.content_type === 'article' && <FileText size={20} className="text-violet-600" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-bold text-sm text-gray-800 mb-1">{content.title}</p>
                      {content.description && (
                        <p className="text-xs text-gray-600 mb-2">{content.description}</p>
                      )}
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs bg-violet-100 text-violet-700 px-2 py-0.5 rounded-full capitalize">
                          {content.content_type}
                        </span>
                        {content.tags.map(tag => (
                          <span key={tag} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">
                            {tag}
                          </span>
                        ))}
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-400">
                          {new Date(content.created_at).toLocaleDateString()}
                        </span>
                        <div className="flex items-center gap-3">
                          <span className="flex items-center gap-1 text-xs text-gray-400">
                            <ThumbsUp size={11} /> {content.like_count}
                          </span>
                          <span className="flex items-center gap-1 text-xs text-gray-400">
                            👁 {content.view_count}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                  {content.content_type === 'photo' && content.content_url && (
                    <img
                      src={`http://localhost:8001${content.content_url}`}
                      alt={content.title}
                      className="w-full h-48 object-cover rounded-xl mt-3"
                    />
                  )}
                  {content.content_type === 'article' && content.content_text && (
                    <div className="mt-3 p-3 bg-gray-50 rounded-xl">
                      <p className="text-sm text-gray-700 line-clamp-3">{content.content_text}</p>
                    </div>
                  )}
                </div>
              ))
            )}
          </>
        )}
      </div>
    </div>
  )
}
