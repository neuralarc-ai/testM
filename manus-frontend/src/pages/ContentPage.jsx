import React, { useEffect, useState } from 'react'
import { useTask } from '../contexts/TaskContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Upload,
  Search,
  Filter,
  MoreVertical,
  Download,
  Trash2,
  Eye,
  Share,
  Copy,
  FileText,
  Image,
  Video,
  Music,
  File,
  Folder,
  Calendar,
  HardDrive,
  Loader2,
  Plus,
} from 'lucide-react'

const ContentPage = () => {
  const { content, loadContent, uploadContent, deleteContent } = useTask()
  const [searchTerm, setSearchTerm] = useState('')
  const [typeFilter, setTypeFilter] = useState('all')
  const [showUploadDialog, setShowUploadDialog] = useState(false)
  const [selectedFiles, setSelectedFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [viewMode, setViewMode] = useState('grid') // grid or list

  useEffect(() => {
    loadContent()
  }, [])

  const contentTypes = [
    { value: 'all', label: 'All Files' },
    { value: 'image', label: 'Images' },
    { value: 'video', label: 'Videos' },
    { value: 'audio', label: 'Audio' },
    { value: 'document', label: 'Documents' },
    { value: 'presentation', label: 'Presentations' },
    { value: 'code', label: 'Code Files' },
    { value: 'data', label: 'Data Files' },
  ]

  const filteredContent = content.filter(item => {
    const matchesSearch = item.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.content_type.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesType = typeFilter === 'all' || item.content_type === typeFilter
    
    return matchesSearch && matchesType
  })

  const getFileIcon = (contentType, filename) => {
    const extension = filename.split('.').pop()?.toLowerCase()
    
    switch (contentType) {
      case 'image':
        return Image
      case 'video':
        return Video
      case 'audio':
        return Music
      case 'document':
        return FileText
      case 'presentation':
        return FileText
      case 'code':
        return FileText
      default:
        return File
    }
  }

  const getFileColor = (contentType) => {
    switch (contentType) {
      case 'image': return 'text-green-600'
      case 'video': return 'text-red-600'
      case 'audio': return 'text-purple-600'
      case 'document': return 'text-blue-600'
      case 'presentation': return 'text-orange-600'
      case 'code': return 'text-gray-600'
      default: return 'text-gray-600'
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const handleFileUpload = async (files) => {
    setUploading(true)
    
    for (const file of files) {
      const contentType = getContentTypeFromFile(file)
      await uploadContent(file, contentType)
    }
    
    setUploading(false)
    setShowUploadDialog(false)
    setSelectedFiles([])
  }

  const getContentTypeFromFile = (file) => {
    const type = file.type
    if (type.startsWith('image/')) return 'image'
    if (type.startsWith('video/')) return 'video'
    if (type.startsWith('audio/')) return 'audio'
    if (type.includes('pdf') || type.includes('document') || type.includes('text')) return 'document'
    if (type.includes('presentation')) return 'presentation'
    return 'document'
  }

  const handleFileSelect = (event) => {
    const files = Array.from(event.target.files)
    setSelectedFiles(files)
  }

  const handleContentAction = async (contentId, action) => {
    switch (action) {
      case 'delete':
        await deleteContent(contentId)
        break
      case 'download':
        // Implement download logic
        console.log('Download content:', contentId)
        break
      case 'share':
        // Implement share logic
        console.log('Share content:', contentId)
        break
      default:
        break
    }
  }

  const groupedContent = filteredContent.reduce((groups, item) => {
    const date = new Date(item.created_at).toDateString()
    if (!groups[date]) {
      groups[date] = []
    }
    groups[date].push(item)
    return groups
  }, {})

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Content Library</h1>
          <p className="text-muted-foreground">
            Manage your files, images, videos, and generated content
          </p>
        </div>
        
        <Dialog open={showUploadDialog} onOpenChange={setShowUploadDialog}>
          <DialogTrigger asChild>
            <Button size="lg" className="gap-2">
              <Upload className="h-5 w-5" />
              Upload Files
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Upload Files</DialogTitle>
              <DialogDescription>
                Select files to upload to your content library
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4">
              <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 text-center">
                <Upload className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <div className="space-y-2">
                  <p className="text-sm font-medium">
                    Drag and drop files here, or click to browse
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Supports images, videos, audio, documents, and more
                  </p>
                </div>
                <input
                  type="file"
                  multiple
                  onChange={handleFileSelect}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
              </div>
              
              {selectedFiles.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-sm font-medium">Selected Files:</h4>
                  <div className="space-y-1">
                    {selectedFiles.map((file, index) => (
                      <div key={index} className="flex items-center justify-between text-sm">
                        <span className="truncate">{file.name}</span>
                        <span className="text-muted-foreground">{formatFileSize(file.size)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              <div className="flex justify-end space-x-2">
                <Button variant="outline" onClick={() => setShowUploadDialog(false)}>
                  Cancel
                </Button>
                <Button 
                  onClick={() => handleFileUpload(selectedFiles)}
                  disabled={selectedFiles.length === 0 || uploading}
                >
                  {uploading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Upload {selectedFiles.length > 0 && `(${selectedFiles.length})`}
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Files</CardTitle>
            <File className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{content.length}</div>
            <p className="text-xs text-muted-foreground">
              Across all types
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Storage Used</CardTitle>
            <HardDrive className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatFileSize(content.reduce((total, item) => total + (item.file_size || 0), 0))}
            </div>
            <p className="text-xs text-muted-foreground">
              Of unlimited storage
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Images</CardTitle>
            <Image className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {content.filter(item => item.content_type === 'image').length}
            </div>
            <p className="text-xs text-muted-foreground">
              Generated & uploaded
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Recent</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {content.filter(item => {
                const dayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000)
                return new Date(item.created_at) > dayAgo
              }).length}
            </div>
            <p className="text-xs text-muted-foreground">
              Last 24 hours
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search files..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <Select value={typeFilter} onValueChange={setTypeFilter}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {contentTypes.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <div className="flex gap-2">
              <Button
                variant={viewMode === 'grid' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('grid')}
              >
                Grid
              </Button>
              <Button
                variant={viewMode === 'list' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('list')}
              >
                List
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Content Display */}
      <div className="space-y-6">
        {Object.keys(groupedContent).length > 0 ? (
          Object.entries(groupedContent).map(([date, items]) => (
            <div key={date} className="space-y-4">
              <h3 className="text-lg font-semibold text-muted-foreground">{date}</h3>
              
              {viewMode === 'grid' ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
                  {items.map((item) => {
                    const FileIcon = getFileIcon(item.content_type, item.filename)
                    
                    return (
                      <Card key={item.id} className="hover:shadow-md transition-shadow group">
                        <CardContent className="p-4">
                          <div className="space-y-3">
                            <div className="flex items-center justify-between">
                              <div className={`w-10 h-10 rounded-lg bg-muted flex items-center justify-center ${getFileColor(item.content_type)}`}>
                                <FileIcon className="h-5 w-5" />
                              </div>
                              
                              <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                  <Button variant="ghost" size="sm" className="opacity-0 group-hover:opacity-100 transition-opacity">
                                    <MoreVertical className="h-4 w-4" />
                                  </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end">
                                  <DropdownMenuItem onClick={() => handleContentAction(item.id, 'download')}>
                                    <Download className="mr-2 h-4 w-4" />
                                    Download
                                  </DropdownMenuItem>
                                  <DropdownMenuItem onClick={() => handleContentAction(item.id, 'share')}>
                                    <Share className="mr-2 h-4 w-4" />
                                    Share
                                  </DropdownMenuItem>
                                  <DropdownMenuItem 
                                    onClick={() => handleContentAction(item.id, 'delete')}
                                    className="text-red-600"
                                  >
                                    <Trash2 className="mr-2 h-4 w-4" />
                                    Delete
                                  </DropdownMenuItem>
                                </DropdownMenuContent>
                              </DropdownMenu>
                            </div>
                            
                            <div>
                              <p className="text-sm font-medium truncate" title={item.filename}>
                                {item.filename}
                              </p>
                              <p className="text-xs text-muted-foreground">
                                {formatFileSize(item.file_size || 0)}
                              </p>
                            </div>
                            
                            <Badge variant="secondary" className="text-xs">
                              {item.content_type}
                            </Badge>
                          </div>
                        </CardContent>
                      </Card>
                    )
                  })}
                </div>
              ) : (
                <div className="space-y-2">
                  {items.map((item) => {
                    const FileIcon = getFileIcon(item.content_type, item.filename)
                    
                    return (
                      <Card key={item.id} className="hover:shadow-sm transition-shadow">
                        <CardContent className="p-4">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-4 flex-1 min-w-0">
                              <div className={`w-10 h-10 rounded-lg bg-muted flex items-center justify-center ${getFileColor(item.content_type)}`}>
                                <FileIcon className="h-5 w-5" />
                              </div>
                              
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium truncate">{item.filename}</p>
                                <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                                  <span>{formatFileSize(item.file_size || 0)}</span>
                                  <span>•</span>
                                  <span>{new Date(item.created_at).toLocaleTimeString()}</span>
                                  <span>•</span>
                                  <Badge variant="secondary" className="text-xs">
                                    {item.content_type}
                                  </Badge>
                                </div>
                              </div>
                            </div>
                            
                            <DropdownMenu>
                              <DropdownMenuTrigger asChild>
                                <Button variant="ghost" size="sm">
                                  <MoreVertical className="h-4 w-4" />
                                </Button>
                              </DropdownMenuTrigger>
                              <DropdownMenuContent align="end">
                                <DropdownMenuItem onClick={() => handleContentAction(item.id, 'download')}>
                                  <Download className="mr-2 h-4 w-4" />
                                  Download
                                </DropdownMenuItem>
                                <DropdownMenuItem onClick={() => handleContentAction(item.id, 'share')}>
                                  <Share className="mr-2 h-4 w-4" />
                                  Share
                                </DropdownMenuItem>
                                <DropdownMenuItem 
                                  onClick={() => handleContentAction(item.id, 'delete')}
                                  className="text-red-600"
                                >
                                  <Trash2 className="mr-2 h-4 w-4" />
                                  Delete
                                </DropdownMenuItem>
                              </DropdownMenuContent>
                            </DropdownMenu>
                          </div>
                        </CardContent>
                      </Card>
                    )
                  })}
                </div>
              )}
            </div>
          ))
        ) : (
          <Card>
            <CardContent className="pt-6">
              <div className="text-center py-12">
                <Folder className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No content found</h3>
                <p className="text-muted-foreground mb-4">
                  {searchTerm || typeFilter !== 'all'
                    ? 'Try adjusting your search or filters'
                    : 'Upload your first file or create content with AI agents'
                  }
                </p>
                {!searchTerm && typeFilter === 'all' && (
                  <Button onClick={() => setShowUploadDialog(true)}>
                    <Plus className="mr-2 h-4 w-4" />
                    Upload Files
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}

export default ContentPage

