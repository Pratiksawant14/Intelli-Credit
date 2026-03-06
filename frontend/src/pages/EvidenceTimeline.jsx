import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Globe, AlertTriangle, ArrowRight, Loader2 } from 'lucide-react';
import { fetchEvidence } from '../api';
import { useAppContext } from '../context/AppContext';

export default function EvidenceTimeline() {
    const { sessionData, updateSession } = useAppContext();
    const navigate = useNavigate();

    const defaultEntity = sessionData.nlpEntities?.find(e => e.type === 'ORG')?.text || 'Orbit Holdings';

    const [searchTerm, setSearchTerm] = useState(defaultEntity);
    const [query, setQuery] = useState('');
    const [isSearching, setIsSearching] = useState(false);
    const [evidence, setEvidence] = useState(sessionData.evidence || []);

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!searchTerm) return;

        setIsSearching(true);
        try {
            const results = await fetchEvidence(searchTerm, query);
            setEvidence(results.results || []);
            updateSession({ evidence: results.results || [] });
        } catch (err) {
            console.error(err);
        } finally {
            setIsSearching(false);
        }
    };

    return (
        <div className="flex flex-col gap-8 w-full max-w-5xl mx-auto py-10 animate-in fade-in slide-in-from-bottom-8 duration-700">
            <header className="flex justify-between items-end">
                <div>
                    <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-400 tracking-tight mb-2">
                        External Intelligence Vector Search
                    </h1>
                    <p className="text-slate-400 text-lg">Gather deep web and news evidence connected via NLP entities</p>
                </div>
                <button
                    className="btn-primary flex items-center gap-2"
                    onClick={() => navigate('/cam')}
                >
                    Generate Final CAM <ArrowRight size={18} />
                </button>
            </header>

            {/* Search Input Panel */}
            <form onSubmit={handleSearch} className="glass-panel p-2 flex flex-col md:flex-row gap-4 items-center relative z-10">
                <div className="flex-1 w-full bg-slate-900/50 rounded-lg flex items-center px-4 py-3 border border-slate-700/50 focus-within:border-blue-500/50 transition duration-300">
                    <Globe className="text-slate-500 mr-3" size={20} />
                    <input
                        type="text"
                        placeholder="Entity Name (e.g. Orbit Holdings)"
                        className="bg-transparent border-none outline-none w-full text-slate-200 placeholder-slate-500 font-medium"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>

                <div className="flex-1 w-full bg-slate-900/50 rounded-lg flex items-center px-4 py-3 border border-slate-700/50 focus-within:border-blue-500/50 transition duration-300">
                    <Search className="text-slate-500 mr-3" size={20} />
                    <input
                        type="text"
                        placeholder="Semantic Query (optional, e.g. 'legal default')"
                        className="bg-transparent border-none outline-none w-full text-slate-200 placeholder-slate-500"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                    />
                </div>

                <button type="submit" className="btn-primary md:w-auto w-full flex justify-center items-center py-3 px-8 mx-2" disabled={isSearching}>
                    {isSearching ? <Loader2 className="animate-spin" size={20} /> : 'Crawl & Index'}
                </button>
            </form>

            {/* Evidence Timeline */}
            {evidence.length > 0 ? (
                <div className="relative pl-8 md:pl-0 mt-6 before:absolute before:inset-0 before:ml-5 md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-blue-500/50 before:via-indigo-500/20 before:to-transparent z-0">
                    {evidence.map((item, idx) => (
                        <div key={idx} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group mb-8">
                            {/* Timeline marker */}
                            <div className="absolute left-0 md:left-1/2 -ml-3 md:-ml-4 w-6 h-6 md:w-8 md:h-8 rounded-full bg-slate-900 border-4 border-blue-500/50 shadow-[0_0_15px_rgba(59,130,246,0.5)] z-10 group-hover:bg-blue-500 group-hover:scale-125 transition-all duration-300"></div>

                            <div className="glass-panel w-full md:w-[45%] p-6 ml-6 md:ml-0 hover:-translate-y-1 transition duration-300 shadow-xl shadow-blue-900/10">
                                <div className="flex justify-between items-start mb-3 border-b border-slate-700/30 pb-3">
                                    <span className="text-xs font-bold uppercase tracking-wider text-blue-400 bg-blue-500/10 px-3 py-1 rounded-full">{item.source || 'News Source'}</span>
                                    <span className="text-xs text-slate-500">{new Date().toLocaleDateString()}</span>
                                </div>
                                <h3 className="text-lg font-bold text-slate-200 mb-2 leading-tight">
                                    <a href={item.url} target="_blank" rel="noreferrer" className="hover:text-blue-400 transition">{item.title}</a>
                                </h3>
                                <p className="text-sm text-slate-400 line-clamp-3 mb-4">{item.content}</p>

                                {/* Risk Tags */}
                                {item.tags && item.tags.length > 0 && (
                                    <div className="flex flex-wrap gap-2">
                                        {item.tags.map(tag => (
                                            <span key={tag} className="flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded bg-red-500/10 text-red-400 border border-red-500/20">
                                                <AlertTriangle size={12} /> {tag}
                                            </span>
                                        ))}
                                    </div>
                                )}
                                {item.search_distance && (
                                    <div className="mt-3 text-right">
                                        <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">L2 Distance: {item.search_distance}</span>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="flex flex-col items-center justify-center p-20 text-slate-500 border border-dashed border-slate-700/50 rounded-2xl glass-panel">
                    <Globe size={48} className="mb-4 opacity-20" />
                    <h3 className="text-xl">No evidence found yet.</h3>
                    <p className="text-sm mt-2">Enter an entity name and crawl sources to build a risk profile.</p>
                </div>
            )}
        </div>
    );
}
