import React, { useState, useCallback, lazy, Suspense } from 'react';
import { PlusIcon } from '@heroicons/react/24/solid';
import { debounce } from 'lodash';
import { ToastProvider, useToast } from './contexts/ToastContext';
import FileInput from './components/FileInput';
import LoadingSpinner from './components/LoadingSpinner';

// Lazy load the Modal component
const Modal = lazy(() => import('./components/Modal'));

function AppContent() {
  const { showToast } = useToast();
  const [formData, setFormData] = useState({
    request: '',
    filePaths: [''],
    currentProblem: '',
    bugFilePath: '',
    solutionFilePath: ''
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [showPopup, setShowPopup] = useState(false);
  const [promptText, setPromptText] = useState('');

  const validateField = useCallback(debounce((field, value) => {
    if (!value.trim()) {
      setErrors(prev => ({
        ...prev,
        [field]: `${field.charAt(0).toUpperCase() + field.slice(1)} is required`
      }));
    } else {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  }, 300), []);

  const addFilePath = useCallback(() => {
    if (formData.filePaths.length < 10) {
      setFormData(prev => ({
        ...prev,
        filePaths: [...prev.filePaths, '']
      }));
    }
  }, [formData.filePaths.length]);

  const handleFilePathChange = useCallback((index, value) => {
    setFormData(prev => {
      const newFilePaths = [...prev.filePaths];
      newFilePaths[index] = value;
      return {
        ...prev,
        filePaths: newFilePaths
      };
    });
  }, []);

  const removeFilePath = useCallback((index) => {
    setFormData(prev => ({
      ...prev,
      filePaths: prev.filePaths.filter((_, i) => i !== index)
    }));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate all fields
    const newErrors = {};
    if (!formData.request.trim()) newErrors.request = 'Request is required';
    if (!formData.currentProblem.trim()) newErrors.currentProblem = 'Current problem is required';
    if (!formData.bugFilePath.trim()) newErrors.bugFilePath = 'Bug file path is required';
    if (!formData.solutionFilePath.trim()) newErrors.solutionFilePath = 'Solution file path is required';

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      showToast('Please fill in all required fields', 'error');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'An error occurred');
      }

      setPromptText(data.prompt);
      setShowPopup(true);
      showToast('Request processed successfully', 'success');
    } catch (error) {
      console.error('Error:', error);
      showToast(error.message || 'An error occurred', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(promptText)
      .then(() => showToast('Copied to clipboard!', 'success'))
      .catch(() => showToast('Failed to copy to clipboard', 'error'));
  }, [promptText, showToast]);

  return (
    <div className="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12">
      <div className="relative py-3 sm:max-w-xl sm:mx-auto">
        <div className="relative px-4 py-10 bg-white shadow-lg sm:rounded-3xl sm:p-20">
          <div className="max-w-md mx-auto">
            <div className="divide-y divide-gray-200">
              <div className="py-8 text-base leading-6 space-y-4 text-gray-700 sm:text-lg sm:leading-7">
                <form onSubmit={handleSubmit} className="space-y-6">
                  {/* Request Field */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Request *
                    </label>
                    <textarea
                      required
                      className={`mt-1 block w-full rounded-md sm:text-sm ${
                        errors.request
                          ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
                          : 'border-gray-300 focus:ring-indigo-500 focus:border-indigo-500'
                      }`}
                      value={formData.request}
                      onChange={(e) => {
                        setFormData(prev => ({ ...prev, request: e.target.value }));
                        validateField('request', e.target.value);
                      }}
                      rows="3"
                      placeholder="Enter your request here"
                    />
                    {errors.request && (
                      <p className="mt-2 text-sm text-red-600">{errors.request}</p>
                    )}
                  </div>

                  {/* File Paths */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      File Paths
                    </label>
                    {formData.filePaths.map((path, index) => (
                      <FileInput
                        key={index}
                        index={index}
                        value={path}
                        onChange={handleFilePathChange}
                        onRemove={removeFilePath}
                      />
                    ))}
                    {formData.filePaths.length < 10 && (
                      <button
                        type="button"
                        onClick={addFilePath}
                        className="mt-2 inline-flex items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded text-indigo-700 bg-indigo-100 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                      >
                        <PlusIcon className="h-5 w-5 mr-1" />
                        Add File Path
                      </button>
                    )}
                  </div>

                  {/* Current Problem Field */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Current Problem *
                    </label>
                    <textarea
                      required
                      className={`mt-1 block w-full rounded-md sm:text-sm ${
                        errors.currentProblem
                          ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
                          : 'border-gray-300 focus:ring-indigo-500 focus:border-indigo-500'
                      }`}
                      value={formData.currentProblem}
                      onChange={(e) => {
                        setFormData(prev => ({ ...prev, currentProblem: e.target.value }));
                        validateField('currentProblem', e.target.value);
                      }}
                      rows="3"
                      placeholder="Describe your current problem"
                    />
                    {errors.currentProblem && (
                      <p className="mt-2 text-sm text-red-600">{errors.currentProblem}</p>
                    )}
                  </div>

                  {/* Bug File Path */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Bug File Path *
                    </label>
                    <input
                      type="text"
                      required
                      className={`mt-1 block w-full rounded-md sm:text-sm ${
                        errors.bugFilePath
                          ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
                          : 'border-gray-300 focus:ring-indigo-500 focus:border-indigo-500'
                      }`}
                      value={formData.bugFilePath}
                      onChange={(e) => {
                        setFormData(prev => ({ ...prev, bugFilePath: e.target.value }));
                        validateField('bugFilePath', e.target.value);
                      }}
                      placeholder="Enter bug file path"
                    />
                    {errors.bugFilePath && (
                      <p className="mt-2 text-sm text-red-600">{errors.bugFilePath}</p>
                    )}
                  </div>

                  {/* Solution File Path */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Solution File Path *
                    </label>
                    <input
                      type="text"
                      required
                      className={`mt-1 block w-full rounded-md sm:text-sm ${
                        errors.solutionFilePath
                          ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
                          : 'border-gray-300 focus:ring-indigo-500 focus:border-indigo-500'
                      }`}
                      value={formData.solutionFilePath}
                      onChange={(e) => {
                        setFormData(prev => ({ ...prev, solutionFilePath: e.target.value }));
                        validateField('solutionFilePath', e.target.value);
                      }}
                      placeholder="Enter solution file path"
                    />
                    {errors.solutionFilePath && (
                      <p className="mt-2 text-sm text-red-600">{errors.solutionFilePath}</p>
                    )}
                  </div>

                  {/* Submit Button */}
                  <div>
                    <button
                      type="submit"
                      disabled={loading}
                      className={`w-full flex justify-center items-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 ${
                        loading ? 'opacity-50 cursor-not-allowed' : ''
                      }`}
                    >
                      {loading ? (
                        <>
                          <LoadingSpinner size="sm" />
                          <span className="ml-2">Processing...</span>
                        </>
                      ) : (
                        'Submit'
                      )}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Modal */}
      <Suspense fallback={null}>
        {showPopup && (
          <Modal
            isOpen={showPopup}
            onClose={() => setShowPopup(false)}
            title="Generated Prompt"
            content={promptText}
            onCopy={handleCopy}
          />
        )}
      </Suspense>
    </div>
  );
}

function App() {
  return (
    <ToastProvider>
      <AppContent />
    </ToastProvider>
  );
}

export default App; 