import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Layout from '@/components/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2, ArrowLeft, FileText, FileSpreadsheet, FileType, Image, Sparkles, BookOpen } from 'lucide-react';

interface NoteFile {
  filename: string;
  format: string;
  size: number;
}

interface NotesData {
  filename: string;
  content: string;
  format: string;
}

interface AnalysisData {
  summary: string;
  highlighted_html: string;
}

const NotesViewer: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [files, setFiles] = useState<NoteFile[]>([]);
  const [currentNote, setCurrentNote] = useState<NotesData | null>(null);
  const [selectedFilename, setSelectedFilename] = useState<string | null>(location.state?.filename || null);
  const [loading, setLoading] = useState(true);
  const [fileLoading, setFileLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Study Mode state
  const [studyMode, setStudyMode] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<AnalysisData | null>(null);

  useEffect(() => {
    const fetchFileList = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/notes/list');
        if (!response.ok) throw new Error('Failed to fetch file list');
        const data = await response.json();
        setFiles(data.files);

        // If no file is selected but files exist, select the first one
        if (!selectedFilename && data.files.length > 0) {
          setSelectedFilename(data.files[0].filename);
        }
      } catch (err) {
        console.error('Failed to fetch files', err);
        setError('Failed to load file list');
      } finally {
        setLoading(false);
      }
    };

    fetchFileList();
  }, []);

  useEffect(() => {
    const fetchNoteContent = async () => {
      if (!selectedFilename) return;

      setFileLoading(true);
      setStudyMode(false);
      setAnalysis(null);

      try {
        const response = await fetch('http://localhost:5000/api/notes', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ filename: selectedFilename })
        });

        if (!response.ok) throw new Error('Failed to fetch notes');
        const data = await response.json();
        setCurrentNote(data);
      } catch (err) {
        console.error('Failed to fetch notes', err);
        setError('Failed to load note content');
      } finally {
        setFileLoading(false);
      }
    };

    fetchNoteContent();
  }, [selectedFilename]);

  const handleAnalyze = async () => {
    if (!selectedFilename || !currentNote) return;

    setAnalyzing(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:5000/api/notes/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename: selectedFilename })
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.error || 'Analysis failed');
      }

      const data = await response.json();
      setAnalysis({
        summary: data.summary,
        highlighted_html: data.highlighted_html
      });
      setStudyMode(true);
    } catch (err: any) {
      console.error('Failed to analyze notes', err);
      setError(err.message || 'Failed to analyze notes');
    } finally {
      setAnalyzing(false);
    }
  };

  const getFormatIcon = (format: string) => {
    switch (format?.toLowerCase()) {
      case 'csv': return <FileSpreadsheet className="w-5 h-5" />;
      case 'docx': return <FileType className="w-5 h-5" />;
      case 'image':
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
      case 'webp':
        return <Image className="w-5 h-5" />;
      default: return <FileText className="w-5 h-5" />;
    }
  };

  const isTextFormat = (format: string) => {
    return ['txt', 'docx', 'md'].includes(format?.toLowerCase());
  };

  const renderContent = () => {
    if (fileLoading) {
      return (
        <div className="flex flex-col items-center justify-center p-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary mb-4" />
          <p className="font-medium">Loading content...</p>
        </div>
      );
    }

    if (!currentNote) return <div className="p-12 text-center text-muted-foreground">Select a file to view its content</div>;

    // Image format
    if (currentNote.format === 'image') {
      return (
        <div className="flex justify-center">
          <img
            src={currentNote.content}
            alt={currentNote.filename}
            className="max-w-full max-h-[600px] object-contain border-2 border-black shadow-neo"
          />
        </div>
      );
    }

    // CSV format
    if (currentNote.format === 'csv') {
      const lines = currentNote.content.split('\n').filter(line => line.trim());
      const rows = lines.map(line => line.split(',').map(cell => cell.trim()));

      return (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse border-2 border-black">
            <tbody>
              {rows.map((row, rowIndex) => (
                <tr key={rowIndex} className={rowIndex === 0 ? 'bg-primary/20' : ''}>
                  {row.map((cell, cellIndex) => (
                    <td
                      key={cellIndex}
                      className={`border-2 border-black px-4 py-2 ${rowIndex === 0 ? 'font-bold' : ''}`}
                    >
                      {cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }

    // Study Mode with highlights
    if (studyMode && analysis) {
      return (
        <div className="space-y-6">
          {/* Summary Card */}
          <div className="bg-gradient-to-r from-purple-100 to-pink-100 p-4 rounded-lg border-2 border-black shadow-neo-sm">
            <div className="flex items-center gap-2 mb-2">
              <BookOpen className="w-5 h-5" />
              <h4 className="font-bold font-display uppercase text-sm">Summary</h4>
            </div>
            <p className="text-sm leading-relaxed">{analysis.summary}</p>
          </div>

          {/* Highlighted Content */}
          <div
            className="prose prose-sm max-w-none bg-white p-4 rounded-lg border-2 border-black"
            dangerouslySetInnerHTML={{ __html: analysis.highlighted_html }}
          />

          {/* Legend */}
          <div className="flex flex-wrap gap-3 p-3 bg-gray-50 rounded-lg border-2 border-black">
            <span className="text-xs font-bold uppercase">Legend:</span>
            <span className="text-xs px-2 py-1 rounded highlight-definition">Definition</span>
            <span className="text-xs px-2 py-1 rounded highlight-concept">Key Concept</span>
            <span className="text-xs px-2 py-1 rounded highlight-important">Important</span>
            <span className="text-xs px-2 py-1 rounded highlight-example">Example</span>
          </div>
        </div>
      );
    }

    // Default text view
    return (
      <pre className="whitespace-pre-wrap font-mono text-sm bg-gray-50 p-4 rounded-lg border-2 border-black overflow-x-auto">
        {currentNote.content}
      </pre>
    );
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex flex-col items-center justify-center space-y-6 h-[60vh]">
          <div className="w-24 h-24 bg-secondary rounded-full border-4 border-black flex items-center justify-center animate-bounce shadow-neo">
            <Loader2 className="h-12 w-12 animate-spin text-black" />
          </div>
          <h2 className="text-3xl font-display font-bold">Initializing Vault...</h2>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      {/* Highlight styles */}
      <style>{`
        .highlight-definition {
          background-color: #fef08a;
          padding: 2px 4px;
          border-radius: 4px;
        }
        .highlight-concept {
          background-color: #bbf7d0;
          padding: 2px 4px;
          border-radius: 4px;
        }
        .highlight-important {
          background-color: #fecaca;
          padding: 2px 4px;
          border-radius: 4px;
        }
        .highlight-example {
          background-color: #bfdbfe;
          padding: 2px 4px;
          border-radius: 4px;
        }
      `}</style>

      <div className="space-y-6 w-full max-w-6xl">
        <div className="flex items-center justify-between">
          <Button
            variant="outline"
            onClick={() => navigate(-1)}
            className="border-2 border-black shadow-neo-sm hover:shadow-neo transition-all"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Topics
          </Button>
          {error && <p className="text-red-600 font-bold bg-red-50 px-4 py-2 border-2 border-black shadow-neo-sm">{error}</p>}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar - File List */}
          <div className="lg:col-span-1 space-y-4">
            <h3 className="font-display font-bold text-xl uppercase tracking-tight">Your Vault</h3>
            <div className="space-y-2">
              {files.map((file) => (
                <div
                  key={file.filename}
                  onClick={() => setSelectedFilename(file.filename)}
                  className={`
                    p-3 border-2 border-black cursor-pointer transition-all duration-200 flex items-center gap-3
                    ${selectedFilename === file.filename
                      ? 'bg-primary shadow-neo-sm translate-x-1'
                      : 'bg-white hover:bg-gray-50 shadow-neo-sm'}
                  `}
                >
                  <div className={`p-2 rounded border border-black ${selectedFilename === file.filename ? 'bg-white' : 'bg-secondary/20'}`}>
                    {getFormatIcon(file.format)}
                  </div>
                  <div className="overflow-hidden">
                    <p className="font-bold text-sm truncate">{file.filename}</p>
                    <p className="text-[10px] uppercase font-mono opacity-60">{(file.size / 1024).toFixed(1)} KB</p>
                  </div>
                </div>
              ))}
              {files.length === 0 && (
                <div className="p-4 border-2 border-dashed border-gray-400 text-center">
                  <p className="text-sm text-muted-foreground">No files found</p>
                </div>
              )}
            </div>
          </div>

          {/* Main Content - Viewer */}
          <div className="lg:col-span-3 space-y-4">
            <Card className="border-2 border-black shadow-neo bg-white min-h-[500px]">
              <CardHeader className="border-b-2 border-black bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-primary/20 border-2 border-black flex items-center justify-center">
                      {getFormatIcon(currentNote?.format || '')}
                    </div>
                    <div className="overflow-hidden">
                      <CardTitle className="font-display truncate max-w-md">{currentNote?.filename || 'Select a file'}</CardTitle>
                      <p className="text-sm text-muted-foreground font-mono uppercase text-xs">{currentNote?.format || '-'}</p>
                    </div>
                  </div>

                  {/* Study Mode Toggle */}
                  {currentNote && isTextFormat(currentNote.format) && (
                    <div className="flex gap-2">
                      {studyMode ? (
                        <Button
                          variant="outline"
                          onClick={() => setStudyMode(false)}
                          className="border-2 border-black"
                        >
                          Exit Study Mode
                        </Button>
                      ) : (
                        <Button
                          onClick={handleAnalyze}
                          disabled={analyzing}
                          className="border-2 border-black bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:from-purple-600 hover:to-pink-600"
                        >
                          {analyzing ? (
                            <>
                              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                              Analyzing...
                            </>
                          ) : (
                            <>
                              <Sparkles className="w-4 h-4 mr-2" />
                              Study Mode
                            </>
                          )}
                        </Button>
                      )}
                    </div>
                  )}
                </div>
              </CardHeader>
              <CardContent className="p-6">
                {renderContent()}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default NotesViewer;
