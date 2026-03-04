import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import UploadPage from './pages/UploadPage';
import ScoreView from './pages/ScoreView';
import EvidenceTimeline from './pages/EvidenceTimeline';
import CAMGenerator from './pages/CAMGenerator';

import HistoryView from './pages/HistoryView';

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<UploadPage />} />
        <Route path="/score" element={<ScoreView />} />
        <Route path="/evidence" element={<EvidenceTimeline />} />
        <Route path="/cam" element={<CAMGenerator />} />
        <Route path="/history" element={<HistoryView />} />
      </Route>
    </Routes>
  );
}

export default App;
