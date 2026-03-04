import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Activity, ShieldAlert, Cpu, CheckCircle } from 'lucide-react';
import { scoreCompany } from '../api';
import { useAppContext } from '../context/AppContext';

export default function ScoreView() {
    const { sessionData, updateSession } = useAppContext();
    const [data, setData] = useState(sessionData.scoreResult || null);
    const [loading, setLoading] = useState(!sessionData.scoreResult);
    const navigate = useNavigate();

    useEffect(() => {
        if (!sessionData.scoreResult && loading) {
            runScore();
        }
    }, [loading]);

    const runScore = async () => {
        try {
            // Typically we'd pass raw_text and document_data properly 
            const payload = {
                raw_text: sessionData.rawText || "No text provided.",
                document_data: sessionData.features || {}
            };

            const response = await scoreCompany(payload);
            setData(response);
            updateSession({
                scoreResult: response.score_result,
                nlpEntities: response.nlp_entities,
                explanation: response.explanation
            });
        } catch (err) {
            console.error(err);
            setLoading(false);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex w-full h-[60vh] flex-col items-center justify-center text-slate-400 font-bold gap-4">
                <Cpu className="animate-spin text-blue-500 w-16 h-16" />
                <h2 className="text-2xl mt-4 animate-pulse">Running ML Engine...</h2>
                <p>Extracting Features • Analyzing NLP Flags • SHAP Explainers</p>
            </div>
        );
    }

    if (!data && !sessionData.scoreResult) {
        return (
            <div className="p-8 text-center text-slate-500">
                <h2>No parsing data found. Go upload documents first.</h2>
            </div>
        );
    }

    // Handle re-render from context
    const curData = data || sessionData;
    const score = curData.score_result?.predicted_score || curData.predicted_score || 0;
    const decision = curData.score_result?.decision || curData.decision || "Unknown";
    const shapFeatures = curData.explanation?.top_features || curData.score_result?.top_features || [];
    const entities = curData.nlp_entities || [];

    return (
        <div className="flex flex-col gap-8 w-full max-w-5xl mx-auto py-10 animate-in fade-in slide-in-from-bottom-8 duration-700">
            <header className="flex justify-between items-end">
                <div>
                    <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400 tracking-tight mb-2">
                        Credit Intelligence Risk Score
                    </h1>
                    <p className="text-slate-400 text-lg">LightGBM Model outputs with SHAP explainability</p>
                </div>
                <button className="btn-primary" onClick={() => navigate('/evidence')}>Next: External Research</button>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                {/* Main Score Glass Card */}
                <div className="glass-panel p-8 col-span-1 lg:col-span-1 flex flex-col items-center justify-center relative overflow-hidden text-center group">
                    <div className={`absolute top-0 w-full h-1 ${decision === 'Approve' ? 'bg-emerald-500' : decision === 'Watchlist' ? 'bg-yellow-500' : 'bg-red-500'}`}></div>
                    <Activity className="absolute -right-4 -bottom-4 w-32 h-32 text-slate-800 opacity-20 pointer-events-none group-hover:scale-110 transition-transform duration-1000" />

                    <h2 className="text-sm uppercase tracking-widest text-slate-400 mb-6 font-semibold">Predicted Score</h2>
                    <div className="relative">
                        <svg className="w-40 h-40 transform -rotate-90">
                            <circle cx="80" cy="80" r="70" stroke="currentColor" strokeWidth="8" fill="transparent" className="text-slate-800" />
                            <circle cx="80" cy="80" r="70" stroke="currentColor" strokeWidth="8" fill="transparent"
                                strokeDasharray={440} strokeDashoffset={440 - (440 * score)}
                                className={`${decision === 'Approve' ? 'text-emerald-500' : decision === 'Watchlist' ? 'text-yellow-500' : 'text-red-500'} transition-all duration-1000 ease-out`} />
                        </svg>
                        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-4xl font-extrabold text-white">
                            {Math.round(score * 100)}
                        </div>
                    </div>

                    <div className={`mt-6 inline-flex px-4 py-1.5 rounded-full font-bold text-sm border shadow-[0_0_15px_currentColor] 
            ${decision === 'Approve' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/50' :
                            decision === 'Watchlist' ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/50' :
                                'bg-red-500/10 text-red-400 border-red-500/50'}`}>
                        {decision}
                    </div>
                </div>

                {/* SHAP Chart */}
                <div className="glass-panel p-8 col-span-1 lg:col-span-2">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="p-2 bg-blue-500/20 text-blue-400 rounded-md">
                            <ShieldAlert size={20} />
                        </div>
                        <h2 className="text-xl font-bold text-slate-200">SHAP Feature Explainability</h2>
                    </div>
                    <div className="h-[250px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={shapFeatures} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                                <XAxis type="number" stroke="#94a3b8" />
                                <YAxis dataKey="feature" type="category" width={150} tick={{ fill: '#cbd5e1', fontSize: 12 }} />
                                <Tooltip cursor={{ fill: 'rgba(255,255,255,0.05)' }} contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }} />
                                <Bar dataKey="impact" radius={[0, 4, 4, 0]}>
                                    {shapFeatures.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.impact < 0 ? '#10b981' : '#ef4444'} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                    <p className="text-xs text-slate-500 mt-2 text-right px-4">Green = Reduces Risk • Red = Increases Risk</p>
                </div>
            </div>

            {/* NLP Detected Entities */}
            <div className="glass-panel p-8 relative hidden md:block">
                <h3 className="text-lg font-bold text-slate-200 mb-6 flex items-center gap-2">
                    <CheckCircle className="text-emerald-400" /> Identified Risk Entities (NLP)
                </h3>
                <div className="flex flex-wrap gap-3">
                    {entities.map((ent, i) => (
                        <div key={i} className={`px-4 py-2 border rounded-full text-sm font-medium flex gap-2 items-center
                ${ent.type === 'LAW' ? 'bg-red-500/10 border-red-500/30 text-red-300' :
                                ent.type === 'MONEY' ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300' :
                                    'bg-blue-500/10 border-blue-500/30 text-blue-300'}`}>
                            <span className="opacity-60 text-xs">{ent.type}</span>
                            {ent.text}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
