import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/services/api'
import toast from 'react-hot-toast'
import { Heart, MessageCircle, Plus } from 'lucide-react'
import { useAuthStore } from '@/hooks/useAuthStore'

const FALLBACK_GROUPS = [
  { id:'1', name:'PCOS Mental Health Circle',       description:'Safe space for emotional support', emoji:'💜', category:'mental_health', color_hex:'#6B3D6E', member_count:3200, joined: true  },
  { id:'2', name:'Hormone-Friendly Recipes',        description:'Share and discover PCOS-friendly meals', emoji:'🥗', category:'nutrition', color_hex:'#7BAE8C', member_count:8100, joined: false },
  { id:'3', name:'Move & Heal — Exercise for PCOS', description:'Workouts adapted for PCOS bodies', emoji:'🏃', category:'fitness',      color_hex:'#E8506A', member_count:5400, joined: false },
  { id:'4', name:'Sleep & Stress Support',          description:'Rest, recover, reduce cortisol',   emoji:'🌙', category:'wellness',     color_hex:'#F4956A', member_count:2900, joined: false },
  { id:'5', name:'PCOS & Fertility Journey',        description:'Navigating fertility with PCOS',   emoji:'🌸', category:'fertility',    color_hex:'#C4622A', member_count:1800, joined: false },
]

const FALLBACK_POSTS: Record<string, any[]> = {
  '1': [
    { id:'p1', content:'I finally feel like myself again after 3 months on this plan! The spearmint tea really helps with mood swings 💜', like_count:284, comment_count:42, author_name:'Priya S.' },
    { id:'p2', content:'Therapy + diet changes have been life-changing. You\'re all so strong 🌸', like_count:198, comment_count:31, author_name:'Meera R.' },
  ],
  '2': [
    { id:'p3', content:'Made the turmeric smoothie bowl and WOW — PCOS game changer. Low GI and so filling 🌿', like_count:521, comment_count:78, author_name:'Sarah K.' },
  ],
}

export default function CommunityPage() {
  const [activeGroup, setActiveGroup] = useState<string | null>(null)
  const [newPost, setNewPost]         = useState('')
  const [joinedMap, setJoinedMap]     = useState<Record<string, boolean>>(
    Object.fromEntries(FALLBACK_GROUPS.map(g => [g.id, g.joined]))
  )
  const { user } = useAuthStore()

  const { data: groups = FALLBACK_GROUPS } = useQuery({
    queryKey: ['groups'],
    queryFn: () => api.get('/community/groups').then(r => r.data).catch(() => FALLBACK_GROUPS),
  })

  const group = groups.find((g: any) => g.id === activeGroup)
  const posts  = FALLBACK_POSTS[activeGroup ?? ''] ?? []

  const toggleJoin = (id: string) => {
    setJoinedMap(j => ({ ...j, [id]: !j[id] }))
    toast.success(joinedMap[id] ? 'Left group' : 'Joined group! 🎉')
  }

  if (activeGroup && group) {
    return (
      <div className="pb-6">
        {/* Group header */}
        <div className="px-5 pt-14 pb-6 text-white" style={{ background: `linear-gradient(135deg, ${group.color_hex}, #2D1F22)` }}>
          <button onClick={() => setActiveGroup(null)} className="text-white/70 text-sm mb-3">← Back</button>
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-white/20 flex items-center justify-center text-2xl">{group.emoji}</div>
            <div>
              <h1 className="font-bold text-lg leading-tight">{group.name}</h1>
              <p className="text-xs opacity-75">{group.member_count?.toLocaleString()} members</p>
            </div>
          </div>
        </div>

        {/* New post */}
        <div className="mx-5 mt-4 card p-4">
          <textarea
            value={newPost}
            onChange={e => setNewPost(e.target.value)}
            placeholder="Share something with the group..."
            className="w-full text-sm text-gray-700 bg-cream rounded-xl p-3 outline-none resize-none border border-plum/10 min-h-[80px]"
          />
          <div className="flex justify-end mt-2">
            <button
              onClick={() => { if (newPost.trim()) { toast.success('Post shared! 🌸'); setNewPost('') } }}
              className="px-4 py-2 bg-rose text-white rounded-full text-sm font-bold flex items-center gap-1"
            >
              <Plus size={14} /> Post
            </button>
          </div>
        </div>

        {/* Posts */}
        <div className="px-5 mt-4 space-y-4">
          {posts.map((post: any) => (
            <div key={post.id} className="card p-4">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-rose to-plum flex items-center justify-center text-white text-xs font-bold">
                  {post.author_name?.[0]}
                </div>
                <p className="text-sm font-semibold text-gray-700">{post.author_name}</p>
              </div>
              <p className="text-sm text-gray-700 leading-relaxed bg-cream rounded-xl p-3">{post.content}</p>
              <div className="flex gap-4 mt-3">
                <button className="flex items-center gap-1.5 text-xs text-gray-400 font-semibold" onClick={() => toast.success('❤️')}>
                  <Heart size={14} /> {post.like_count}
                </button>
                <button className="flex items-center gap-1.5 text-xs text-gray-400 font-semibold">
                  <MessageCircle size={14} /> {post.comment_count}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="pb-6">
      {/* Header */}
      <div className="bg-gradient-to-br from-peach to-orange-700 text-white px-6 pt-14 pb-6">
        <h1 className="font-serif text-3xl italic mb-1">Community 🤝</h1>
        <p className="text-sm opacity-80">You're not alone — 42,000+ women with PCOS</p>
      </div>

      <div className="px-5 mt-5 space-y-4">
        {groups.map((g: any) => (
          <div key={g.id} className="card p-4">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-11 h-11 rounded-2xl flex items-center justify-center text-2xl" style={{ background: g.color_hex + '22' }}>
                {g.emoji}
              </div>
              <div className="flex-1">
                <p className="font-bold text-sm text-gray-800 leading-tight">{g.name}</p>
                <p className="text-xs text-gray-400">{g.member_count?.toLocaleString()} members</p>
              </div>
              <button
                onClick={() => toggleJoin(g.id)}
                className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all ${
                  joinedMap[g.id] ? 'bg-sage-light text-green-700' : 'bg-peach-light text-peach'
                }`}
              >
                {joinedMap[g.id] ? 'Joined ✓' : 'Join'}
              </button>
            </div>
            <p className="text-xs text-gray-500 bg-cream rounded-xl p-3">{g.description}</p>
            <button
              onClick={() => setActiveGroup(g.id)}
              className="mt-3 w-full text-center text-xs font-bold text-plum py-2 rounded-xl bg-plum-light"
            >
              View Posts →
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
