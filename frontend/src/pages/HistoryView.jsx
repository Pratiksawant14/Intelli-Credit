import { useState, useEffect } from 'react';
import { History, FileText, Download, Target, CheckCircle2, AlertTriangle, XCircle, Search } from 'lucide-react';
import { fetchCamHistory } from '../api';
import { useAppContext } from '../context/AppContext';

export default function HistoryView() {
    const { sessionData } = useAppContext();
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadHistory = async () => {
            try {
                const data = await fetchCamHistory(sessionData?.user?.id);
                setHistory(data);
            } catch (err) {
                console.error("Failed to load History:", err);
            } finally {
                setLoading(false);
            }
        };
        loadHistory();
    }, []);

    const getStatusIcon = (disposition) => {
        switch (disposition?.toLowerCase()) {
            case 'approve': return <CheckCircle2 className="text-emerald-500" size={20} />;
            case 'watchlist': return <AlertTriangle className="text-amber-500" size={20} />;
            case 'reject': return <XCircle className="text-rose-500" size={20} />;
            default: return <Target className="text-slate-500" size={20} />;
        }
    };

    const formatDate = (ds) => {
        if (!ds) return 'N/A';
        const d = new Date(ds);
        return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    return (
        <div className="flex flex-col gap-8 w-full max-w-6xl mx-auto py-10 animate-in fade-in duration-500">
            <header className="flex justify-between items-end border-b border-slate-700/50 pb-6">
                <div>
                    <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400 tracking-tight mb-2 flex items-center gap-3">
                        <History className="text-indigo-400" size={36} /> Credit Memo History
                    </h1>
                    <p className="text-slate-400 text-lg">Immutable ledger of all generated Credit Appraisal Memos from Supabase</p>
                </div>
                <div className="glass-panel px-4 py-2 flex gap-2 items-center text-slate-300">
                    <Search size={18} className="text-slate-500" />
                    <span className="font-mono text-sm">{history.length} Records securely fetched</span>
                </div>
            </header>

            <div className="glass-panel overflow-hidden border border-slate-700/50 shadow-2xl relative">
                {loading ? (
                    <div className="flex items-center justify-center h-64 text-slate-400 gap-4">
                        <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                        Querying Supabase Postgres...
                    </div>
                ) : history.length === 0 ? (
                    <div className="flex flex-col items-center justify-center p-16 text-center">
                        <div className="w-20 h-20 rounded-full bg-slate-800 flex items-center justify-center mb-6 text-slate-600">
                            <FileText size={40} />
                        </div>
                        <h3 className="text-2xl font-bold text-slate-300 mb-2">No Reports Generated Yet.</h3>
                        <p className="text-slate-500 max-w-md">Once you synthesize a Credit Appraisal Memo in the CAM Generation tab, it will be securely logged to Postgres and tracked here.</p>
                    </div>
                ) : (
                    <div className="overflow-x-auto w-full">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-slate-900/80 border-b border-slate-700/80">
                                    <th className="py-5 px-6 font-semibold uppercase tracking-wider text-xs text-slate-400">Target Entity</th>
                                    <th className="py-5 px-6 font-semibold uppercase tracking-wider text-xs text-slate-400 text-center">ML Score</th>
                                    <th className="py-5 px-6 font-semibold uppercase tracking-wider text-xs text-slate-400">Disposition</th>
                                    <th className="py-5 px-6 font-semibold uppercase tracking-wider text-xs text-slate-400">Execution Date</th>
                                    <th className="py-5 px-6 font-semibold text-right uppercase tracking-wider text-xs text-slate-400">Record Pointer</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-800/60">
                                {history.map((record) => (
                                    <tr key={record.id} className="hover:bg-slate-800/40 transition-colors group">
                                        <td className="py-5 px-6 font-medium text-slate-200">
                                            {record.company_name}
                                        </td>
                                        <td className="py-5 px-6 text-center">
                                            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-slate-800 text-slate-300 border border-slate-700">
                                                {record.credit_score}
                                            </span>
                                        </td>
                                        <td className="py-5 px-6">
                                            <div className="flex items-center gap-2 font-medium capitalize text-slate-300">
                                                {getStatusIcon(record.disposition)}
                                                {record.disposition}
                                            </div>
                                        </td>
                                        <td className="py-5 px-6 text-slate-400 text-sm font-mono">
                                            {formatDate(record.generated_at)}
                                        </td>
                                        <td className="py-5 px-6 text-right">
                                            {record.pdf_path ? (
                                                <a
                                                    href={`${import.meta.env.VITE_API_BASE_URL}/${record.pdf_path.replace(/\\/g, '/')}`}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-indigo-600/10 text-indigo-400 hover:bg-indigo-600/20 hover:text-indigo-300 border border-indigo-500/20 transition-all ml-auto focus:outline-none opacity-80 hover:opacity-100"
                                                    title="Download this specific CAM Report"
                                                >
                                                    <Download size={16} /> Download PDF
                                                </a>
                                            ) : (
                                                <span className="text-slate-500 text-sm italic">No file attached</span>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
}
