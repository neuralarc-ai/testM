import React, { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Progress } from '@/components/ui/progress'
import {
  User,
  Mail,
  Calendar,
  MapPin,
  Globe,
  Edit,
  Save,
  X,
  Camera,
  Zap,
  Crown,
  Star,
  TrendingUp,
  Award,
  Target,
  Clock,
} from 'lucide-react'

const ProfilePage = () => {
  const { user, updateProfile } = useAuth()
  const [editing, setEditing] = useState(false)
  const [loading, setLoading] = useState(false)
  const [profileData, setProfileData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    bio: user?.bio || '',
    location: user?.location || '',
    website: user?.website || '',
    company: user?.company || '',
    job_title: user?.job_title || '',
  })

  const handleChange = (e) => {
    setProfileData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
  }

  const handleSave = async () => {
    setLoading(true)
    const result = await updateProfile(profileData)
    if (result.success) {
      setEditing(false)
    }
    setLoading(false)
  }

  const handleCancel = () => {
    setProfileData({
      first_name: user?.first_name || '',
      last_name: user?.last_name || '',
      email: user?.email || '',
      bio: user?.bio || '',
      location: user?.location || '',
      website: user?.website || '',
      company: user?.company || '',
      job_title: user?.job_title || '',
    })
    setEditing(false)
  }

  const getSubscriptionColor = (type) => {
    switch (type) {
      case 'premium': return 'bg-blue-500 text-white'
      case 'enterprise': return 'bg-purple-500 text-white'
      default: return 'bg-gray-500 text-white'
    }
  }

  const getSubscriptionIcon = (type) => {
    switch (type) {
      case 'premium': return Crown
      case 'enterprise': return Star
      default: return Zap
    }
  }

  // Mock data for achievements and stats
  const achievements = [
    { id: 1, title: 'First Task', description: 'Completed your first AI task', icon: Target, earned: true },
    { id: 2, title: 'Power User', description: 'Created 50+ tasks', icon: TrendingUp, earned: true },
    { id: 3, title: 'Content Creator', description: 'Generated 100+ images', icon: Award, earned: false },
    { id: 4, title: 'Code Master', description: 'Built 10+ applications', icon: Award, earned: false },
  ]

  const stats = [
    { label: 'Tasks Completed', value: 127, icon: Target },
    { label: 'Credits Used', value: 2450, icon: Zap },
    { label: 'Days Active', value: 45, icon: Clock },
    { label: 'Success Rate', value: '94%', icon: TrendingUp },
  ]

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Profile</h1>
        <p className="text-muted-foreground">
          Manage your account information and preferences
        </p>
      </div>

      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList>
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="subscription">Subscription</TabsTrigger>
          <TabsTrigger value="achievements">Achievements</TabsTrigger>
          <TabsTrigger value="stats">Statistics</TabsTrigger>
        </TabsList>

        {/* Profile Tab */}
        <TabsContent value="profile" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Personal Information</CardTitle>
                  <CardDescription>
                    Update your profile details and personal information
                  </CardDescription>
                </div>
                {!editing ? (
                  <Button onClick={() => setEditing(true)} variant="outline">
                    <Edit className="mr-2 h-4 w-4" />
                    Edit
                  </Button>
                ) : (
                  <div className="flex space-x-2">
                    <Button onClick={handleCancel} variant="outline" size="sm">
                      <X className="mr-2 h-4 w-4" />
                      Cancel
                    </Button>
                    <Button onClick={handleSave} size="sm" disabled={loading}>
                      <Save className="mr-2 h-4 w-4" />
                      Save
                    </Button>
                  </div>
                )}
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Avatar Section */}
              <div className="flex items-center space-x-6">
                <div className="relative">
                  <Avatar className="h-24 w-24">
                    <AvatarImage src={user?.avatar_url} />
                    <AvatarFallback className="text-lg">
                      {user?.first_name?.[0]}{user?.last_name?.[0]} || {user?.username?.[0]?.toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  {editing && (
                    <Button
                      size="sm"
                      className="absolute -bottom-2 -right-2 rounded-full h-8 w-8 p-0"
                    >
                      <Camera className="h-4 w-4" />
                    </Button>
                  )}
                </div>
                <div>
                  <h3 className="text-lg font-semibold">
                    {user?.first_name && user?.last_name 
                      ? `${user.first_name} ${user.last_name}`
                      : user?.username
                    }
                  </h3>
                  <p className="text-muted-foreground">{user?.email}</p>
                  <div className="flex items-center space-x-2 mt-2">
                    <Badge className={getSubscriptionColor(user?.subscription_type)}>
                      {React.createElement(getSubscriptionIcon(user?.subscription_type), { className: "h-3 w-3 mr-1" })}
                      {user?.subscription_type?.toUpperCase()}
                    </Badge>
                    <span className="text-sm text-muted-foreground">
                      Member since {new Date(user?.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>

              {/* Form Fields */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="first_name">First Name</Label>
                  <Input
                    id="first_name"
                    name="first_name"
                    value={profileData.first_name}
                    onChange={handleChange}
                    disabled={!editing}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="last_name">Last Name</Label>
                  <Input
                    id="last_name"
                    name="last_name"
                    value={profileData.last_name}
                    onChange={handleChange}
                    disabled={!editing}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    value={profileData.email}
                    onChange={handleChange}
                    disabled={!editing}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="location">Location</Label>
                  <Input
                    id="location"
                    name="location"
                    value={profileData.location}
                    onChange={handleChange}
                    disabled={!editing}
                    placeholder="City, Country"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="company">Company</Label>
                  <Input
                    id="company"
                    name="company"
                    value={profileData.company}
                    onChange={handleChange}
                    disabled={!editing}
                    placeholder="Your company"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="job_title">Job Title</Label>
                  <Input
                    id="job_title"
                    name="job_title"
                    value={profileData.job_title}
                    onChange={handleChange}
                    disabled={!editing}
                    placeholder="Your role"
                  />
                </div>

                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="website">Website</Label>
                  <Input
                    id="website"
                    name="website"
                    value={profileData.website}
                    onChange={handleChange}
                    disabled={!editing}
                    placeholder="https://yourwebsite.com"
                  />
                </div>

                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="bio">Bio</Label>
                  <Textarea
                    id="bio"
                    name="bio"
                    value={profileData.bio}
                    onChange={handleChange}
                    disabled={!editing}
                    placeholder="Tell us about yourself..."
                    rows={4}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Subscription Tab */}
        <TabsContent value="subscription" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Subscription Details</CardTitle>
              <CardDescription>
                Manage your subscription and billing information
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between p-6 border rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className={`w-12 h-12 rounded-lg ${getSubscriptionColor(user?.subscription_type)} flex items-center justify-center`}>
                    {React.createElement(getSubscriptionIcon(user?.subscription_type), { className: "h-6 w-6" })}
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold">
                      {user?.subscription_type?.charAt(0).toUpperCase() + user?.subscription_type?.slice(1)} Plan
                    </h3>
                    <p className="text-muted-foreground">
                      {user?.subscription_type === 'free' && 'Basic features with 300 monthly credits'}
                      {user?.subscription_type === 'premium' && 'Advanced features with 1,000 monthly credits'}
                      {user?.subscription_type === 'enterprise' && 'Full access with 5,000 monthly credits'}
                    </p>
                  </div>
                </div>
                {user?.subscription_type === 'free' && (
                  <Button>Upgrade Plan</Button>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="space-y-2">
                  <Label>Credits Balance</Label>
                  <div className="text-2xl font-bold">{user?.credits_balance}</div>
                  <Progress 
                    value={(user?.credits_balance / (user?.subscription_type === 'free' ? 300 : user?.subscription_type === 'premium' ? 1000 : 5000)) * 100} 
                    className="w-full"
                  />
                </div>

                <div className="space-y-2">
                  <Label>Next Billing</Label>
                  <div className="text-lg font-medium">
                    {new Date(new Date().getFullYear(), new Date().getMonth() + 1, 1).toLocaleDateString()}
                  </div>
                  <p className="text-sm text-muted-foreground">Credits reset monthly</p>
                </div>

                <div className="space-y-2">
                  <Label>Status</Label>
                  <Badge variant="secondary" className="bg-green-100 text-green-800">
                    Active
                  </Badge>
                  <p className="text-sm text-muted-foreground">Auto-renewal enabled</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Achievements Tab */}
        <TabsContent value="achievements" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Achievements</CardTitle>
              <CardDescription>
                Track your progress and unlock new milestones
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {achievements.map((achievement) => (
                  <div
                    key={achievement.id}
                    className={`p-4 border rounded-lg ${
                      achievement.earned ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                        achievement.earned ? 'bg-green-500 text-white' : 'bg-gray-400 text-white'
                      }`}>
                        <achievement.icon className="h-5 w-5" />
                      </div>
                      <div className="flex-1">
                        <h4 className="font-medium">{achievement.title}</h4>
                        <p className="text-sm text-muted-foreground">{achievement.description}</p>
                      </div>
                      {achievement.earned && (
                        <Badge variant="secondary" className="bg-green-100 text-green-800">
                          Earned
                        </Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Statistics Tab */}
        <TabsContent value="stats" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {stats.map((stat, index) => (
              <Card key={index}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">{stat.label}</CardTitle>
                  <stat.icon className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stat.value}</div>
                  <p className="text-xs text-muted-foreground">
                    Since joining
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Activity Overview</CardTitle>
              <CardDescription>
                Your usage patterns and trends
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span>Task Completion Rate</span>
                    <span>94%</span>
                  </div>
                  <Progress value={94} className="w-full" />
                </div>
                
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span>Credit Efficiency</span>
                    <span>87%</span>
                  </div>
                  <Progress value={87} className="w-full" />
                </div>
                
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span>Agent Utilization</span>
                    <span>76%</span>
                  </div>
                  <Progress value={76} className="w-full" />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default ProfilePage

