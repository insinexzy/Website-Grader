import React, { useState } from 'react';
import axios from 'axios';
import { ArrowUpTrayIcon, ChartBarIcon } from '@heroicons/react/24/outline';
import LoadingSpinner from './components/LoadingSpinner';
import ResultsModal from './components/ResultsModal';

// Get API URL from environment variable or default to localhost
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function App() {
  const [url, setUrl] = useState('');
  const [urls, setUrls] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [showModal, setShowModal] = useState(false);

  const handleUrlChange = (e) => {
    setUrl(e.target.value);
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const text = e.target.result;
        const uploadedUrls = text.split('\n').filter(url => url.trim());
        setUrls(uploadedUrls);
      };
      reader.readAsText(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      const urlsToAnalyze = urls.length > 0 ? urls : [url];
      console.log('Making request to:', `${API_URL}/api/analyze`);
      console.log('With payload:', { url: urlsToAnalyze[0] });
      
      const response = await axios.post(`${API_URL}/api/analyze`, {
        url: urlsToAnalyze[0] // Currently only analyzing first URL
      });
      
      setResults(response.data);
      setShowModal(true);
    } catch (error) {
      console.error('Error analyzing website:', error);
      const errorMessage = error.response?.data?.message || error.message || 'Error analyzing website. Please try again.';
      alert(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h1 className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
            Website Grader
          </h1>
          <p className="mt-2 text-lg text-gray-600">
            Analyze your website's technology stack, performance, and modernization needs
          </p>
        </div>

        <div className="mt-12">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="url" className="block text-sm font-medium text-gray-700">
                Website URL
              </label>
              <div className="mt-1">
                <input
                  type="url"
                  name="url"
                  id="url"
                  value={url}
                  onChange={handleUrlChange}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  placeholder="https://example.com"
                />
              </div>
            </div>

            <div className="text-center">
              <span className="text-sm text-gray-500">OR</span>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Upload URLs File
              </label>
              <div className="mt-1 flex justify-center rounded-md border-2 border-dashed border-gray-300 px-6 pt-5 pb-6">
                <div className="space-y-1 text-center">
                  <ArrowUpTrayIcon className="mx-auto h-12 w-12 text-gray-400" />
                  <div className="flex text-sm text-gray-600">
                    <label htmlFor="file-upload" className="relative cursor-pointer rounded-md bg-white font-medium text-indigo-600 focus-within:outline-none focus-within:ring-2 focus-within:ring-indigo-500 focus-within:ring-offset-2 hover:text-indigo-500">
                      <span>Upload a file</span>
                      <input
                        id="file-upload"
                        name="file-upload"
                        type="file"
                        accept=".txt"
                        className="sr-only"
                        onChange={handleFileUpload}
                      />
                    </label>
                    <p className="pl-1">or drag and drop</p>
                  </div>
                  <p className="text-xs text-gray-500">
                    TXT file with one URL per line
                  </p>
                </div>
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={isLoading || (!url && urls.length === 0)}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Analyzing...' : 'Check Score'}
              </button>
            </div>
          </form>
        </div>
      </div>

      {isLoading && <LoadingSpinner />}
      {showModal && (
        <ResultsModal
          results={results}
          onClose={() => setShowModal(false)}
        />
      )}
    </div>
  );
}

export default App; 