import { useState } from 'react';
import { Shield, Mail, Lock, LogIn, UserPlus } from 'lucide-react';
import { loginUser, registerUser } from '../api';
import { useAppContext } from '../context/AppContext';

export default function LoginPage() {
    const { updateSession } = useAppContext();
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            if (isLogin) {
                const data = await loginUser({ email, password });
                updateSession({ user: { id: data.user_id, email: data.email } });
            } else {
                const data = await registerUser({ email, password });
                updateSession({ user: { id: data.user_id, email: data.email } });
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Authentication failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex h-screen w-full bg-[#0a0f1d] items-center justify-center overflow-hidden text-slate-200 selection:bg-blue-500/30">
            {/* Global decorative background elements */}
            <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-[100px] pointer-events-none"></div>
            <div className="absolute bottom-0 left-0 w-[30rem] h-[30rem] bg-emerald-500/10 rounded-full blur-[120px] pointer-events-none"></div>

            <div className="glass-panel w-full max-w-md p-8 relative z-10 animate-in zoom-in-95 duration-500 border border-slate-700/50 shadow-2xl">
                <div className="flex flex-col items-center justify-center mb-8 gap-4">
                    <div className="w-16 h-16 bg-blue-500/20 text-blue-400 rounded-2xl flex items-center justify-center shadow-[0_0_30px_rgba(59,130,246,0.3)]">
                        <Shield size={32} />
                    </div>
                    <div className="text-center">
                        <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400 tracking-tight">
                            Intelli-Credit
                        </h1>
                        <p className="text-slate-400 text-sm mt-1">AI-Powered Appraisal Engine</p>
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="flex flex-col gap-5">
                    {error && (
                        <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-sm text-red-400 text-center animate-pulse">
                            {error}
                        </div>
                    )}

                    <div className="flex flex-col gap-2">
                        <label className="text-sm font-semibold text-slate-400 tracking-wide uppercase">Email Address</label>
                        <div className="relative">
                            <Mail size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                            <input
                                type="email"
                                required
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full bg-slate-900/50 text-slate-200 pl-10 pr-4 py-3 rounded-xl border border-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                                placeholder="analyst@bank.com"
                            />
                        </div>
                    </div>

                    <div className="flex flex-col gap-2 mb-2">
                        <label className="text-sm font-semibold text-slate-400 tracking-wide uppercase">Password</label>
                        <div className="relative">
                            <Lock size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                            <input
                                type="password"
                                required
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                minLength={6}
                                className="w-full bg-slate-900/50 text-slate-200 pl-10 pr-4 py-3 rounded-xl border border-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                                placeholder="••••••••"
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="btn-primary w-full flex items-center justify-center gap-3 bg-gradient-to-r from-blue-600 to-emerald-600 hover:from-blue-500 hover:to-emerald-500 border-none shadow-[0_0_20px_rgba(16,185,129,0.3)] hover:shadow-[0_0_30px_rgba(16,185,129,0.5)] py-3 rounded-xl font-bold text-lg disabled:opacity-50"
                    >
                        {isLogin ? (
                            <><LogIn size={20} /> Sign In</>
                        ) : (
                            <><UserPlus size={20} /> Create Account</>
                        )}
                    </button>

                    <div className="text-center mt-2">
                        <button
                            type="button"
                            onClick={() => { setIsLogin(!isLogin); setError(''); }}
                            className="text-slate-400 hover:text-blue-400 text-sm transition-colors"
                        >
                            {isLogin ? "Don't have an account? Register." : "Already an analyst? Sign In."}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
