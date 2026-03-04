import { createContext, useState, useContext } from 'react';

const AppContext = createContext();

export const AppProvider = ({ children }) => {
    const [sessionData, setSessionData] = useState({
        companyName: '',
        uploadedDocuments: [], // raw responses from upload route
        features: {},
        nlpEntities: [],
        scoreResult: null,
        evidence: [],
        camUrl: null
    });

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
