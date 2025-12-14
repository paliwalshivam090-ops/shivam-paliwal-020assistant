import React, { useState } from 'react';
import { Search, Loader, X, RotateCcw, Settings, Moon, Sun, Palette, Image, Upload } from 'lucide-react';

export default function MultiApp() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const [abortController, setAbortController] = useState(null);
  const [showSettings, setShowSettings] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [theme, setTheme] = useState('blue'); // blue, purple, green, orange, pink
  const [uploadedImage, setUploadedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);

  const themes = {
    blue: {
      light: { bg: 'from-blue-500 to-purple-600', header: 'from-blue-600 to-purple-600', button: 'from-blue-600 to-purple-600', accent: 'blue' },
      dark: { bg: 'from-gray-900 to-blue-900', header: 'from-blue-900 to-purple-900', button: 'from-blue-700 to-purple-700', accent: 'blue' }
    },
    purple: {
      light: { bg: 'from-purple-500 to-pink-600', header: 'from-purple-600 to-pink-600', button: 'from-purple-600 to-pink-600', accent: 'purple' },
      dark: { bg: 'from-gray-900 to-purple-900', header: 'from-purple-900 to-pink-900', button: 'from-purple-700 to-pink-700', accent: 'purple' }
    },
    green: {
      light: { bg: 'from-green-500 to-teal-600', header: 'from-green-600 to-teal-600', button: 'from-green-600 to-teal-600', accent: 'green' },
      dark: { bg: 'from-gray-900 to-green-900', header: 'from-green-900 to-teal-900', button: 'from-green-700 to-teal-700', accent: 'green' }
    },
    orange: {
      light: { bg: 'from-orange-500 to-red-600', header: 'from-orange-600 to-red-600', button: 'from-orange-600 to-red-600', accent: 'orange' },
      dark: { bg: 'from-gray-900 to-orange-900', header: 'from-orange-900 to-red-900', button: 'from-orange-700 to-red-700', accent: 'orange' }
    },
    pink: {
      light: { bg: 'from-pink-500 to-rose-600', header: 'from-pink-600 to-rose-600', button: 'from-pink-600 to-rose-600', accent: 'pink' },
      dark: { bg: 'from-gray-900 to-pink-900', header: 'from-pink-900 to-rose-900', button: 'from-pink-700 to-rose-700', accent: 'pink' }
    }
  };

  const currentTheme = themes[theme][darkMode ? 'dark' : 'light'];

  // Stop search function
  const stopSearch = () => {
    if (abortController) {
      abortController.abort();
    }
    setIsSearching(false);
  };

  // Clear and reset function
  const clearSearch = () => {
    setSearchQuery('');
    setSearchResults(null);
    setIsSearching(false);
    setUploadedImage(null);
    setImagePreview(null);
  };

  // Handle image upload
  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
        setUploadedImage(reader.result.split(',')[1]); // Get base64 data
      };
      reader.readAsDataURL(file);
    }
  };

  // Remove uploaded image
  const removeImage = () => {
    setUploadedImage(null);
    setImagePreview(null);
  };

  // Search function
  const handleSearch = async () => {
    if (!searchQuery.trim() && !uploadedImage) return;
    
    setIsSearching(true);
    setSearchResults(null);
    
    const controller = new AbortController();
    setAbortController(controller);
    
    try {
      // Build message content
      const messageContent = [];
      
      // Add image if uploaded
      if (uploadedImage) {
        messageContent.push({
          type: "image",
          source: {
            type: "base64",
            media_type: "image/jpeg",
            data: uploadedImage
          }
        });
      }
      
      // Add text query
      if (searchQuery.trim()) {
        messageContent.push({
          type: "text",
          text: searchQuery
        });
      } else if (uploadedImage) {
        messageContent.push({
          type: "text",
          text: "What's in this image? Please describe it in detail."
        });
      }

      const response = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 1000,
          tools: uploadedImage ? undefined : [{
            type: "web_search_20250305",
            name: "web_search"
          }],
          messages: [{
            role: "user",
            content: messageContent
          }]
        }),
        signal: controller.signal
      });

      const data = await response.json();
      
      const fullResponse = data.content
        .map(item => {
          if (item.type === "text") {
            return item.text;
          }
          return "";
        })
        .filter(Boolean)
        .join("\n");
      
      setSearchResults(fullResponse || "No results found.");
    } catch (error) {
      if (error.name === 'AbortError') {
        setSearchResults("Search stopped by user.");
      } else {
        setSearchResults("Error performing search. Please try again.");
        console.error("Search error:", error);
      }
    } finally {
      setIsSearching(false);
      setAbortController(null);
    }
  };

  return (
    <div className={`min-h-screen bg-gradient-to-br ${currentTheme.bg} p-4 transition-all duration-500`}>
      <div className={`max-w-2xl mx-auto ${darkMode ? 'bg-gray-800' : 'bg-white'} rounded-2xl shadow-2xl overflow-hidden transition-colors duration-500`}>
        {/* Header */}
        <div className={`bg-gradient-to-r ${currentTheme.header} p-6 text-white relative`}>
          <h1 className="text-3xl font-bold text-center">Shivam Vision</h1>
          <p className={`text-center ${darkMode ? 'text-gray-300' : 'text-blue-100'} mt-2`}>AI-Powered Search & Image Analysis</p>
          <p className={`text-center ${darkMode ? 'text-gray-400' : 'text-blue-200'} text-sm mt-1`}>Created by Shivam</p>
          
          {/* Settings Button */}
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="absolute top-6 right-6 p-2 bg-white bg-opacity-20 rounded-lg hover:bg-opacity-30 transition"
          >
            <Settings size={24} />
          </button>
        </div>

        {/* Settings Panel */}
        {showSettings && (
          <div className={`${darkMode ? 'bg-gray-700 border-gray-600' : 'bg-gray-50 border-gray-200'} border-b-2 p-6 transition-colors duration-500`}>
            <h3 className={`text-lg font-bold mb-4 ${darkMode ? 'text-white' : 'text-gray-800'}`}>Settings</h3>
            
            {/* Dark Mode Toggle */}
            <div className="mb-6">
              <label className={`block text-sm font-semibold mb-3 ${darkMode ? 'text-gray-200' : 'text-gray-700'}`}>
                Display Mode
              </label>
              <div className="flex gap-3">
                <button
                  onClick={() => setDarkMode(false)}
                  className={`flex-1 p-3 rounded-lg font-medium flex items-center justify-center gap-2 transition ${
                    !darkMode
                      ? `bg-${currentTheme.accent}-600 text-white`
                      : `${darkMode ? 'bg-gray-600 text-gray-200' : 'bg-gray-200 text-gray-700'} hover:bg-${currentTheme.accent}-100`
                  }`}
                >
                  <Sun size={20} />
                  Light
                </button>
                <button
                  onClick={() => setDarkMode(true)}
                  className={`flex-1 p-3 rounded-lg font-medium flex items-center justify-center gap-2 transition ${
                    darkMode
                      ? `bg-${currentTheme.accent}-600 text-white`
                      : `${darkMode ? 'bg-gray-600 text-gray-200' : 'bg-gray-200 text-gray-700'} hover:bg-${currentTheme.accent}-100`
                  }`}
                >
                  <Moon size={20} />
                  Dark
                </button>
              </div>
            </div>

            {/* Theme Selection */}
            <div>
              <label className={`block text-sm font-semibold mb-3 ${darkMode ? 'text-gray-200' : 'text-gray-700'}`}>
                <Palette size={16} className="inline mr-2" />
                Color Theme
              </label>
              <div className="grid grid-cols-5 gap-2">
                <button
                  onClick={() => setTheme('blue')}
                  className={`h-12 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 ${
                    theme === 'blue' ? 'ring-4 ring-offset-2 ring-blue-400' : 'opacity-70 hover:opacity-100'
                  } transition`}
                  title="Blue"
                />
                <button
                  onClick={() => setTheme('purple')}
                  className={`h-12 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 ${
                    theme === 'purple' ? 'ring-4 ring-offset-2 ring-purple-400' : 'opacity-70 hover:opacity-100'
                  } transition`}
                  title="Purple"
                />
                <button
                  onClick={() => setTheme('green')}
                  className={`h-12 rounded-lg bg-gradient-to-r from-green-600 to-teal-600 ${
                    theme === 'green' ? 'ring-4 ring-offset-2 ring-green-400' : 'opacity-70 hover:opacity-100'
                  } transition`}
                  title="Green"
                />
                <button
                  onClick={() => setTheme('orange')}
                  className={`h-12 rounded-lg bg-gradient-to-r from-orange-600 to-red-600 ${
                    theme === 'orange' ? 'ring-4 ring-offset-2 ring-orange-400' : 'opacity-70 hover:opacity-100'
                  } transition`}
                  title="Orange"
                />
                <button
                  onClick={() => setTheme('pink')}
                  className={`h-12 rounded-lg bg-gradient-to-r from-pink-600 to-rose-600 ${
                    theme === 'pink' ? 'ring-4 ring-offset-2 ring-pink-400' : 'opacity-70 hover:opacity-100'
                  } transition`}
                  title="Pink"
                />
              </div>
            </div>
          </div>
        )}

        {/* Content Area */}
        <div className={`p-8 ${darkMode ? 'bg-gray-800' : 'bg-white'} transition-colors duration-500`}>
          <div className="space-y-6">
            <div className="text-center mb-8">
              <Search className={`w-20 h-20 mx-auto ${darkMode ? 'text-blue-400' : `text-${currentTheme.accent}-600`} mb-4`} />
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-gray-800'}`}>Shivam Vision Search</h2>
              <p className={`${darkMode ? 'text-gray-400' : 'text-gray-600'} mt-2`}>Ask anything, search with text or upload an image</p>
            </div>

            {/* Image Upload Section */}
            {imagePreview ? (
              <div className={`relative ${darkMode ? 'bg-gray-700 border-gray-600' : 'bg-gray-100 border-gray-300'} border-2 rounded-xl p-4 transition-colors duration-500`}>
                <img src={imagePreview} alt="Uploaded" className="w-full h-64 object-contain rounded-lg" />
                <button
                  onClick={removeImage}
                  className="absolute top-6 right-6 bg-red-600 text-white p-2 rounded-full hover:bg-red-700 transition shadow-lg"
                >
                  <X size={20} />
                </button>
                <p className={`text-center mt-3 text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                  Image uploaded successfully! Add a question or click Search to analyze.
                </p>
              </div>
            ) : (
              <label className={`block ${darkMode ? 'bg-gray-700 border-gray-600 hover:bg-gray-650' : 'bg-gray-50 border-gray-300 hover:bg-gray-100'} border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-300`}>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="hidden"
                />
                <Upload className={`w-12 h-12 mx-auto ${darkMode ? 'text-gray-400' : 'text-gray-400'} mb-3`} />
                <p className={`${darkMode ? 'text-gray-300' : 'text-gray-700'} font-semibold mb-1`}>
                  Upload an Image to Analyze
                </p>
                <p className={`${darkMode ? 'text-gray-400' : 'text-gray-500'} text-sm`}>
                  Click to browse or drag and drop
                </p>
              </label>
            )}
            
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !isSearching && handleSearch()}
              placeholder={uploadedImage ? "Ask a question about the image..." : "Ask anything..."}
              disabled={isSearching}
              className={`w-full p-5 text-lg border-2 ${
                darkMode 
                  ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400 focus:border-blue-500' 
                  : 'bg-white border-gray-300 text-gray-900 focus:border-blue-500'
              } rounded-xl focus:outline-none transition disabled:opacity-50`}
            />
            
            <div className="flex gap-3">
              <button
                onClick={isSearching ? stopSearch : handleSearch}
                disabled={!searchQuery.trim() && !uploadedImage && !isSearching}
                className={`flex-1 text-white p-5 rounded-xl font-bold text-lg flex items-center justify-center gap-3 transition shadow-lg ${
                  isSearching
                    ? 'bg-red-600 hover:bg-red-700'
                    : (!searchQuery.trim() && !uploadedImage)
                    ? 'bg-gray-400 cursor-not-allowed'
                    : `bg-gradient-to-r ${currentTheme.button} hover:opacity-90`
                }`}
              >
                {isSearching ? (
                  <>
                    <X size={24} />
                    Stop Search
                  </>
                ) : (
                  <>
                    {uploadedImage ? <Image size={24} /> : <Search size={24} />}
                    {uploadedImage ? 'Analyze Image' : 'Search'}
                  </>
                )}
              </button>
              
              {(searchResults || searchQuery || uploadedImage) && (
                <button
                  onClick={clearSearch}
                  className={`${
                    darkMode ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-600 hover:bg-gray-700'
                  } text-white p-5 rounded-xl font-bold transition shadow-lg flex items-center gap-2`}
                  title="Clear and start new search"
                >
                  <RotateCcw size={24} />
                </button>
              )}
            </div>

            {/* Search Results */}
            {searchResults && (
              <div className={`mt-8 p-8 ${
                darkMode 
                  ? 'bg-gray-700 border-gray-600' 
                  : 'bg-gradient-to-br from-gray-50 to-blue-50 border-gray-200'
              } rounded-xl border-2 max-h-96 overflow-y-auto shadow-inner transition-colors duration-500`}>
                <h3 className={`font-bold text-xl mb-4 ${darkMode ? 'text-white' : 'text-gray-800'} flex items-center gap-2`}>
                  <Search size={20} />
                  Results:
                </h3>
                <div className={`${darkMode ? 'text-gray-200' : 'text-gray-700'} whitespace-pre-wrap leading-relaxed text-base`}>
                  {searchResults}
                </div>
              </div>
            )}
          </div>
        </div>
        
        {/* Footer */}
        <div className={`${darkMode ? 'bg-gray-900 border-gray-700' : 'bg-gray-100 border-gray-200'} border-t py-4 text-center transition-colors duration-500`}>
          <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
            © 2024 Shivam Vision - Created by Shivam
          </p>
        </div>
      </div>
    </div>
  );
}