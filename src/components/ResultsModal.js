import React from 'react';

const ResultsModal = ({ results, onClose }) => {
  if (!results) return null;

  console.log('Rendering ResultsModal with results:', results);

  // Extract the actual results from the response structure
  const analysisResults = results.results || results;

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  const getProgressBarColor = (score) => {
    if (score >= 80) return 'bg-green-600';
    if (score >= 60) return 'bg-yellow-600';
    return 'bg-red-600';
  };

  const formatScore = (score) => {
    return typeof score === 'number' ? Math.round(score) : score;
  };

  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Analysis Results</h2>
              <p className="mt-1 text-sm text-gray-500">{results.url}</p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500"
            >
              <span className="sr-only">Close</span>
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Overall Score */}
          <div className="mt-6 p-6 bg-gray-50 rounded-lg">
            <div className="flex justify-between items-center">
              <h3 className="text-xl font-semibold text-gray-900">Overall Score</h3>
              <div className={`${getScoreBgColor(analysisResults.total_score)} px-4 py-2 rounded-full`}>
                <span className={`text-2xl font-bold ${getScoreColor(analysisResults.total_score)}`}>
                  {formatScore(analysisResults.total_score)}
                </span>
              </div>
            </div>
            <div className="mt-4 w-full bg-gray-200 rounded-full h-2.5">
              <div
                className={`${getProgressBarColor(analysisResults.total_score)} h-2.5 rounded-full`}
                style={{ width: `${analysisResults.total_score}%` }}
              ></div>
            </div>
          </div>

          {/* Category Scores */}
          {analysisResults.category_scores && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Category Scores</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(analysisResults.category_scores).map(([category, score]) => (
                  <div key={category} className="p-4 bg-white border rounded-lg">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium capitalize">{category.replace(/_/g, ' ')}</span>
                      <span className={`${getScoreColor(score)} font-semibold`}>
                        {formatScore(score)}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`${getProgressBarColor(score)} h-2 rounded-full`}
                        style={{ width: `${score}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Lead Quality */}
          {analysisResults.lead_quality_score && (
            <div className="mt-6 p-6 bg-white border rounded-lg">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Lead Quality Assessment</h3>
              <div className="space-y-3">
                <div className="flex items-center">
                  <span className="font-medium">Priority:</span>
                  <span className="ml-2 px-3 py-1 rounded-full bg-blue-100 text-blue-800">
                    {analysisResults.lead_quality_score.priority}
                  </span>
                </div>
                <p className="text-gray-600">{analysisResults.lead_quality_score.reason}</p>
                <p className="text-gray-600">{analysisResults.lead_quality_score.estimated_work}</p>
              </div>
            </div>
          )}

          {/* Improvement Opportunities */}
          {analysisResults.improvement_opportunities && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Improvement Opportunities</h3>
              <div className="space-y-4">
                {Object.entries(analysisResults.improvement_opportunities).map(([category, items]) => (
                  <div key={category} className="p-4 bg-white border rounded-lg">
                    <h4 className="font-medium capitalize text-gray-900 mb-2">
                      {category.replace(/_/g, ' ')}
                    </h4>
                    <ul className="list-disc list-inside space-y-1">
                      {items.map((item, index) => (
                        <li key={index} className="text-gray-600">{item}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Additional Information */}
          <div className="mt-6 text-sm text-gray-500">
            <p>Analysis completed at: {analysisResults.timestamp || results.timestamp}</p>
            <p>Response time: {((analysisResults.load_time || results.load_time || 0) * 1000).toFixed(2)}ms</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultsModal; 