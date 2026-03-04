import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { UploadCloud, FileType, CheckCircle, ArrowRight, Loader2 } from 'lucide-react';
import { uploadDocuments } from '../api';
import { useAppContext } from '../context/AppContext';

export default function UploadPage() {
    const [files, setFiles] = useState([]);
    const [isUploading, setIsUploading] = useState(false);
    const [error, setError] = useState(null);
    const { updateSession } = useAppContext();
    const navigate = useNavigate();

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        const droppedFiles = Array.from(e.dataTransfer.files).filter(
            (f) => f.type === 'application/pdf' || f.name.endsWith('.pdf')
        );
        setFiles((prev) => [...prev, ...droppedFiles]);
    }, []);

    const handleFileChange = (e) => {
        if (e.target.files) {
            setFiles((prev) => [...prev, ...Array.from(e.target.files)]);
        }
    };

    const removeFile = (idx) => {
        setFiles(files.filter((_, i) => i !== idx));
    };

    const handleUpload = async () => {
        if (files.length === 0) return;
        setIsUploading(true);
        setError(null);
        try {
            const response = await uploadDocuments(files);

            // We expect the backend to return status: 'success', processed_files: [...]
            // But for the pipeline, let's aggregate all raw text into the session
            const allText = response.processed_files.map(f => {
                let text = f.raw_ocr || "";
                if (f.extracted_text_blocks && f.extracted_text_blocks.length > 0) {
                    text += " " + f.extracted_text_blocks.map(b => b.text).join(' ');
                }
                return text;
            }).join(' ');

            // We save the response and navigate to Score

            // Extract a rudimentary "Company Name" from the first non-empty line of the raw text
            const firstLine = allText.split('\n').map(l => l.trim()).filter(l => l.length > 5)[0] || "Unknown Entity";
            const cleanCompanyName = firstLine.replace(/[^a-zA-Z0-9\s]/g, '').slice(0, 50).trim();

            updateSession({
                companyName: cleanCompanyName,
                uploadedDocuments: response.processed_files,
                rawText: allText,
                features: {}, // Send empty, backend will use Regex to extract real financial features from rawText.

                // Clear out OLD run states so ScoreView recalculates
                scoreResult: null,
                nlpEntities: [],
                evidence: [],
                camUrl: null
            });
            // Optionally store rawtext or other meta 

            navigate('/score');
        } catch (err) {
            console.error(err);
            setError('Failed to upload and parse documents. Please try again.');
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <div className="flex flex-col gap-8 w-full max-w-4xl mx-auto py-10">
            <header>
                <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400 tracking-tight mb-2">
                    Ingest Financial Documents
                </h1>
                <p className="text-slate-400 text-lg">
                    Upload PDF Annual Reports, GST Returns, or Bank Statements to trigger the smart OCR and Layout Extractor.
                </p>
            </header>

            {error && (
                <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl flex items-center gap-3">
                    <div className="w-2 h-2 rounded-full bg-red-400 animate-pulse"></div>
                    {error}
                </div>
            )}

            <div
                className="glass-panel p-10 flex flex-col items-center justify-center border-dashed border-2 hover:border-blue-500/50 transition-colors duration-300 cursor-pointer min-h-[300px] relative overflow-hidden group"
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleDrop}
                onClick={() => document.getElementById('fileUpload').click()}
            >
                <div className="absolute inset-0 bg-blue-500/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                <input
                    type="file"
                    id="fileUpload"
                    className="hidden"
                    multiple
                    accept="application/pdf"
                    onChange={handleFileChange}
                />

                <div className="w-20 h-20 rounded-full bg-blue-500/10 flex items-center justify-center mb-6 text-blue-400 group-hover:scale-110 group-hover:bg-blue-500/20 transition-all duration-300 shadow-[0_0_30px_rgba(59,130,246,0.2)]">
                    <UploadCloud size={40} />
                </div>
                <h3 className="text-2xl font-bold text-slate-200 mb-2">Drag & Drop PDFs here</h3>
                <p className="text-slate-400 text-center max-w-md">
                    Support for scanned images, multiline tables, and unstructured layouts. PDF format only.
                </p>
                <div className="mt-8 px-6 py-2 rounded-full border border-slate-600 bg-slate-800/50 text-sm font-medium hover:bg-slate-700 transition">
                    Browse Files
                </div>
            </div>

            {files.length > 0 && (
                <div className="glass-panel p-6 animate-in slide-in-from-bottom flex flex-col gap-6">
                    <div className="flex justify-between items-center">
                        <h3 className="text-xl font-bold text-slate-200 flex items-center gap-2">
                            <FileType className="text-emerald-400" />
                            Selected Documents ({files.length})
                        </h3>

                        <button
                            onClick={handleUpload}
                            disabled={isUploading}
                            className="btn-primary flex items-center gap-2"
                        >
                            {isUploading ? (
                                <>
                                    <Loader2 className="animate-spin" size={20} />
                                    Processing...
                                </>
                            ) : (
                                <>
                                    Run OCR Pipeline
                                    <ArrowRight size={20} />
                                </>
                            )}
                        </button>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {files.map((file, idx) => (
                            <div key={idx} className="flex flex-col bg-slate-800/60 rounded-lg p-4 justify-between border border-slate-700/50 relative overflow-hidden group">
                                <div className="flex items-start gap-3 relative z-10">
                                    <div className="p-2 bg-emerald-500/20 text-emerald-400 rounded-md">
                                        <CheckCircle size={20} />
                                    </div>
                                    <div className="overflow-hidden">
                                        <p className="text-sm font-semibold truncate text-slate-200 w-[150px]" title={file.name}>{file.name}</p>
                                        <p className="text-xs text-slate-500 mt-1">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                                    </div>
                                </div>
                                <button
                                    onClick={(e) => { e.stopPropagation(); removeFile(idx); }}
                                    className="absolute top-2 right-2 text-slate-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition"
                                    disabled={isUploading}
                                >
                                    ✕
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
