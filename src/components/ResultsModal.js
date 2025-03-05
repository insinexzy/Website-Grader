import React from 'react';
import { XCircleIcon as XMarkIcon } from '@heroicons/react/24/outline';

function ResultsModal({ results, onClose }) {
  const getScoreColor = (score) => {
    if (score >= 80) return 'text-score-green';
    if (score >= 60) return 'text-score-yellow';
    return 'text-score-red';
  };

  const getScoreBgColor = (score) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  const renderSingleResult = (result, url) => (
    <div key={url} className="bg-white p-6 rounded-lg shadow-lg">
      <div className="flex justify-between items-start">
        <h3 className="text-lg font-semibold text-gray-900">{url}</h3>
        <div className={`${getScoreBgColor(result.total_score)} px-4 py-2 rounded-full`}>
          <span className={`text-2xl font-bold ${getScoreColor(result.total_score)}`}>
            {result.total_score}
          </span>
        </div>
      </div>

      <div className="mt-4">
        <h4 className="font-medium text-gray-700">Category Scores:</h4>
        <div className="mt-2 grid grid-cols-2 gap-4">
          {Object.entries(result.category_scores).map(([category, score]) => (
            <div key={category} className="flex justify-between items-center">
              <span className="capitalize">{category}:</span>
              <span className={getScoreColor(score)}>{score}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-4">
        <h4 className="font-medium text-gray-700">Lead Quality:</h4>
        <div className="mt-2 space-y-2">
          <p className="font-semibold">{result.lead_quality_score.priority}</p>
          <p className="text-sm text-gray-600">{result.lead_quality_score.reason}</p>
          <p className="text-sm text-gray-600">{result.lead_quality_score.estimated_work}</p>
        </div>
      </div>

      {result.improvement_opportunities && (
        <div className="mt-4">
          <h4 className="font-medium text-gray-700">Improvement Opportunities:</h4>
          <div className="mt-2 space-y-2">
            {Object.entries(result.improvement_opportunities).map(([category, items]) => (
              <div key={category} className="ml-4">
                <h5 className="text-sm font-medium capitalize">{category}:</h5>
                <ul className="list-disc list-inside text-sm text-gray-600">
                  {items.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200 sticky top-0 bg-white">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-900">Analysis Results</h2>
            <button
              onClick={onClose}
              className="rounded-full p-2 hover:bg-gray-100 transition-colors"
            >
              <XMarkIcon className="h-6 w-6 text-gray-400" />
            </button>
          </div>
        </div>

        <div className="p-6 space-y-6">
          {typeof results === 'object' && results !== null ? (
            Object.entries(results).map(([url, result]) => renderSingleResult(result, url))
          ) : (
            <p className="text-gray-500">No results available</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default ResultsModal; 