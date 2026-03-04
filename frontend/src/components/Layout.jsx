import { Outlet, NavLink } from 'react-router-dom';
import { UploadCloud, CheckCircle, Search, FileText } from 'lucide-react';

const Sidebar = () => {
    const steps = [
        { name: 'Document Ingestion', path: '/', icon: UploadCloud },
        { name: 'Credit Scoring', path: '/score', icon: CheckCircle },
        { name: 'External Evidence', path: '/evidence', icon: Search },
        { name: 'CAM Generation', path: '/cam', icon: FileText },
    ];

    return (
        <div className="w-64 h-full bg-slate-900 border-r border-slate-700/50 flex flex-col pt-8 px-4 flex-shrink-0 relative overflow-hidden">
            {/* Decorative gradient blob */}
            <div className="absolute top-0 left-0 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl pointer-events-none -translate-x-1/2 -translate-y-1/2"></div>

            <div className="mb-10 z-10 flex items-center gap-2">
                <div className="p-2 bg-blue-500/20 rounded-lg text-blue-400">
                    <FileText size={24} />
                </div>
                <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-300 tracking-tight">
                    Intelli-Credit
                </h1>
            </div>

            <nav className="flex-1 space-y-2 z-10">
                {steps.map((step) => (
                    <NavLink
                        key={step.path}
                        to={step.path}
                        className={({ isActive }) =>
                            `flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-300 font-medium overflow-hidden relative group ` +
                            (isActive
                                ? 'bg-blue-600/10 text-blue-400 border border-blue-500/30 shadow-[0_0_15px_rgba(59,130,246,0.1)]'
                                : 'text-slate-400 hover:text-slate-200 hover:bg-white/5 border border-transparent')
                        }
                    >
                        <step.icon size={18} className="z-10" />
                        <span className="z-10">{step.name}</span>
                        <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-r from-white/0 via-white/5 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700 pointer-events-none"></div>
                    </NavLink>
                ))}
            </nav>

            <div className="mt-auto mb-6 text-xs text-slate-500 z-10 px-4">
                <p>AI Appraised • Secure</p>
                <p>Intelli-Credit Engine v1.0</p>
            </div>
        </div>
    );
};

export default function Layout() {
    return (
        <div className="flex h-screen w-full bg-[#0a0f1d] overflow-hidden text-slate-200 selection:bg-blue-500/30">
            {/* Global decorative background elements */}
            <div className="fixed top-1/4 right-0 w-96 h-96 bg-indigo-500/5 rounded-full blur-[100px] pointer-events-none"></div>
            <div className="fixed bottom-0 left-1/4 w-[30rem] h-[30rem] bg-emerald-500/5 rounded-full blur-[120px] pointer-events-none"></div>

            <Sidebar />
            <div className="flex-1 flex flex-col h-full relative z-10 overflow-hidden">
                <main className="flex-1 overflow-x-hidden overflow-y-auto w-full p-8 custom-scrollbar">
                    <div className="max-w-6xl mx-auto h-full animate-in fade-in duration-500">
                        <Outlet />
                    </div>
                </main>
            </div>
        </div>
    );
}
