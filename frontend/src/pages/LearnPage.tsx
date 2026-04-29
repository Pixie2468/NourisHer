import { useState } from 'react'
import { Play, BookOpen, Clock, ThumbsUp } from 'lucide-react'

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

export default function LearnPage() {
  const [tab, setTab] = useState('videos')
  const [playing, setPlaying] = useState(-1)

  return (
    <div className="pb-6">
      <div className="bg-gradient-to-br from-violet-600 to-indigo-800 text-white px-6 pt-14 pb-6">
        <h1 className="font-serif text-3xl italic mb-1">Learn</h1>
        <p className="text-sm opacity-80">Evidence-based PCOS education</p>
      </div>

      <div className="flex gap-3 px-5 py-4">
        {['videos', 'articles'].map(t => (
          <button key={t} onClick={() => setTab(t)}
            className={"flex-1 py-2.5 rounded-2xl text-sm font-bold capitalize transition-all border " +
              (tab === t ? 'bg-violet-600 text-white border-violet-600' : 'bg-white text-gray-500 border-plum/10')}>
            {t === 'videos' ? 'Videos' : 'Articles'}
          </button>
        ))}
      </div>

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
      </div>
    </div>
  )
}
