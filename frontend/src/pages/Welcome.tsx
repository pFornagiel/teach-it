import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '@/components/Layout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Upload, FileText, Loader2 } from 'lucide-react';
import { Input } from '@/components/ui/input';

const Welcome: React.FC = () => {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:5000/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        // Wait a bit to show loading state (fake "reading" the file)
        setTimeout(() => {
            navigate('/topics', { state: { filename: file.name } });
        }, 1500);
      } else {
        console.error('Upload failed');
        setIsUploading(false);
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      setIsUploading(false);
    }
  };

  return (
    <Layout>
      <div className="space-y-8 text-center">
        <blockquote className="text-2xl font-semibold italic text-muted-foreground">
          "If you want to master something, teach it."
        </blockquote>
        <p className="text-sm text-muted-foreground">— Richard Feynman</p>

        <Card className="mx-auto max-w-md mt-10 shadow-lg border-muted/40">
          <CardHeader>
            <CardTitle>Start Teaching</CardTitle>
            <CardDescription>Upload your notes to begin the session.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid w-full max-w-sm items-center gap-1.5 mx-auto">
                <div className="flex items-center justify-center w-full">
                    <label htmlFor="dropzone-file" className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-lg cursor-pointer bg-gray-50 dark:hover:bg-bray-800 dark:bg-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:hover:border-gray-500 dark:hover:bg-gray-600">
                        <div className="flex flex-col items-center justify-center pt-5 pb-6">
                            {file ? (
                                <>
                                    <FileText className="w-8 h-8 mb-2 text-gray-500 dark:text-gray-400" />
                                    <p className="mb-2 text-sm text-gray-500 dark:text-gray-400 font-semibold">{file.name}</p>
                                </>
                            ) : (
                                <>
                                    <Upload className="w-8 h-8 mb-2 text-gray-500 dark:text-gray-400" />
                                    <p className="mb-2 text-sm text-gray-500 dark:text-gray-400"><span className="font-semibold">Click to upload</span> or drag and drop</p>
                                    <p className="text-xs text-gray-500 dark:text-gray-400">TXT, MD, PDF (text only)</p>
                                </>
                            )}
                        </div>
                        <Input id="dropzone-file" type="file" className="hidden" onChange={handleFileChange} />
                    </label>
                </div>
            </div>

            <Button 
                onClick={handleUpload} 
                disabled={!file || isUploading} 
                className="w-full"
            >
              {isUploading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processing Notes...
                </>
              ) : (
                'Start Session'
              )}
            </Button>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default Welcome;
