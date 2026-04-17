'use client'

import { useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { MessageSquare, TrendingUp, Users, DollarSign, Settings } from 'lucide-react'

type ServiceName = 'whatsapp' | 'instagram' | 'facebook' | 'email' | 'sms'
type Services = Record<ServiceName, boolean>

export default function Dashboard() {
  const [services, setServices] = useState<Services>({
    whatsapp: true,
    instagram: true,
    facebook: true,
    email: true,
    sms: false
  })

  const [conversations] = useState([
    { id: 1, customer: 'John Doe', channel: 'WhatsApp', status: 'Active', lastMessage: '2 min ago' },
    { id: 2, customer: 'Jane Smith', channel: 'Instagram', status: 'Pending', lastMessage: '15 min ago' },
    { id: 3, customer: 'Bob Wilson', channel: 'Facebook', status: 'Active', lastMessage: '1 hour ago' }
  ])

  const [salesData] = useState([
    { name: 'Lead', value: 45 },
    { name: 'Qualified', value: 32 },
    { name: 'Proposal', value: 18 },
    { name: 'Closed', value: 12 }
  ])

  const toggleService = (service: ServiceName) => {
    setServices(prev => {
      const newServices = { ...prev }
      newServices[service] = !newServices[service]
      return newServices
    })
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">1AI Engage Dashboard</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">Total Conversations</p>
                <p className="text-2xl font-bold">{conversations.length}</p>
              </div>
              <MessageSquare className="text-blue-500" size={32} />
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">Active Leads</p>
                <p className="text-2xl font-bold">45</p>
              </div>
              <Users className="text-green-500" size={32} />
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">Conversion Rate</p>
                <p className="text-2xl font-bold">26.7%</p>
              </div>
              <TrendingUp className="text-purple-500" size={32} />
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">Revenue</p>
                <p className="text-2xl font-bold">$12.4K</p>
              </div>
              <DollarSign className="text-yellow-500" size={32} />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Sales Pipeline</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={salesData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4 flex items-center">
              <Settings className="mr-2" size={20} />
              Service Controls
            </h2>
            <div className="space-y-4">
              {(Object.entries(services) as [ServiceName, boolean][]).map(([service, enabled]) => (
                <div key={service} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                  <span className="capitalize font-medium">{service}</span>
                  <button
                    onClick={() => toggleService(service)}
                    className={`px-4 py-2 rounded transition-colors ${
                      enabled 
                        ? 'bg-green-500 text-white hover:bg-green-600' 
                        : 'bg-gray-300 text-gray-700 hover:bg-gray-400'
                    }`}
                  >
                    {enabled ? 'Enabled' : 'Disabled'}
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Recent Conversations</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-3">Customer</th>
                  <th className="text-left p-3">Channel</th>
                  <th className="text-left p-3">Status</th>
                  <th className="text-left p-3">Last Message</th>
                </tr>
              </thead>
              <tbody>
                {conversations.map(conv => (
                  <tr key={conv.id} className="border-b hover:bg-gray-50">
                    <td className="p-3">{conv.customer}</td>
                    <td className="p-3">{conv.channel}</td>
                    <td className="p-3">
                      <span className={`px-2 py-1 rounded text-sm ${
                        conv.status === 'Active' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {conv.status}
                      </span>
                    </td>
                    <td className="p-3 text-gray-500">{conv.lastMessage}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
