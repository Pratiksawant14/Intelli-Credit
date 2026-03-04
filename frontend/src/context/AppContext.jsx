import { createContext, useState, useContext, useEffect } from 'react';

const AppContext = createContext();

export const AppProvider = ({ children }) => {
    // Attempt to load from localStorage first
    const loadInitialState = () => {
        const saved = localStorage.getItem('intelli_credit_session');
        if (saved) {
            try { return JSON.parse(saved); } catch (e) { }
        }
        return {
            companyName: '',
            uploadedDocuments: [],
            features: {},
            nlpEntities: [],
            scoreResult: null,
            evidence: [],
            camUrl: null,
            rawText: ''
        };
    };

    const [sessionData, setSessionData] = useState(loadInitialState);

    // Sync to localStorage on every change
    useEffect(() => {
        localStorage.setItem('intelli_credit_session', JSON.stringify(sessionData));
    }, [sessionData]);

    const updateSession = (updates) => {
        setSessionData(prev => ({ ...prev, ...updates }));
    };

    return (
        <AppContext.Provider value={{ sessionData, updateSession }}>
            {children}
        </AppContext.Provider>
    );
};

export const useAppContext = () => useContext(AppContext);
