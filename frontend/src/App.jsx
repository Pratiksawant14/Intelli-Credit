import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import UploadPage from './pages/UploadPage';
import ScoreView from './pages/ScoreView';
import EvidenceTimeline from './pages/EvidenceTimeline';
import CAMGenerator from './pages/CAMGenerator';

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<UploadPage />} />
        <Route path="/score" element={<ScoreView />} />
        <Route path="/evidence" element={<EvidenceTimeline />} />
        <Route path="/cam" element={<CAMGenerator />} />
      </Route>
    </Routes>
  );
}

export default App;
