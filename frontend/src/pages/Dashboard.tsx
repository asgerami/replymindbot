import { useState, useEffect } from 'react';
import { useAuth, supabase } from '../contexts/AuthContext';
import { Settings, MessageSquare, Activity, Key, Loader2, Save } from 'lucide-react';

export default function Dashboard() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [ownerProfile, setOwnerProfile] = useState<any>(null);
  
  // Dashboard Metrics
  const [stats, setStats] = useState({
    totalCustomers: 0,
    messagesAutoReplied: 0,
    actionRequired: 0
  });

  // Form states
  const [formData, setFormData] = useState({
    owner_name: '',
    telegram_bot_token: '',
    telegram_id: ''
  });

  useEffect(() => {
    if (user) {
      fetchOwnerData();
    }
  }, [user]);

  const fetchOwnerData = async () => {
    try {
      // For MVP: Search by owner_name matching email prefix, or just get the first one they created.
      // Better way is to have an explicit claim or email column, but we will use the user's email as owner_name for new accounts
      let { data, error } = await supabase
        .from('business_owners')
        .select('*')
        .eq('owner_name', user?.email)
        .single();
      
      if (data) {
        setOwnerProfile(data);
        setFormData({
          owner_name: data.owner_name,
          telegram_bot_token: data.telegram_bot_token || '',
          telegram_id: data.telegram_id || ''
        });
        fetchStats(data.id);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async (ownerId: string) => {
    // Basic stats fetching
    const { count: custCount } = await supabase.from('customers').select('*', { count: 'exact', head: true }).eq('business_owner_id', ownerId);
    
    // Auto Replied
    const { count: autoCount } = await supabase.from('messages')
      .select('*, conversations!inner(business_owner_id)', { count: 'exact', head: true })
      .eq('conversations.business_owner_id', ownerId)
      .eq('sender_type', 'Assistant')
      .eq('status', 'Sent');

    // Action Required
    const { count: actionCount } = await supabase.from('messages')
      .select('*, conversations!inner(business_owner_id)', { count: 'exact', head: true })
      .eq('conversations.business_owner_id', ownerId)
      .eq('status', 'Action_Required');

    setStats({
      totalCustomers: custCount || 0,
      messagesAutoReplied: autoCount || 0,
      actionRequired: actionCount || 0
    });
  };

  const handleSaveProfile = async () => {
    setSaving(true);
    try {
      if (ownerProfile) {
        // Update
        const { error } = await supabase.from('business_owners')
          .update({
            telegram_bot_token: formData.telegram_bot_token,
            telegram_id: formData.telegram_id
          })
          .eq('id', ownerProfile.id);
        if (error) throw error;
      } else {
        // Create
        const { data, error } = await supabase.from('business_owners')
          .insert({
            owner_name: user?.email,
            telegram_bot_token: formData.telegram_bot_token,
            telegram_id: formData.telegram_id,
            plan_tier: 'Starter'
          })
          .select()
          .single();
        if (error) throw error;
        setOwnerProfile(data);
      }
      alert('Profile saved successfully!');
    } catch (error: any) {
      alert(error.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-[60vh]">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Welcome, {user?.email}</h1>
      </div>

      {ownerProfile && (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <MessageSquare className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Total Customers</dt>
                    <dd className="text-lg font-medium text-gray-900">{stats.totalCustomers}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Activity className="h-6 w-6 text-green-500" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Auto-Replied Messages</dt>
                    <dd className="text-lg font-medium text-gray-900">{stats.messagesAutoReplied}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
          <div className="bg-white overflow-hidden shadow rounded-lg bg-red-50 border border-red-100">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Settings className="h-6 w-6 text-red-500 animate-pulse" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-red-800 truncate">Action Required</dt>
                    <dd className="text-lg font-bold text-red-600">{stats.actionRequired}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white shadow sm:rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4 flex items-center">
            <Key className="w-5 h-5 mr-2 text-primary-500" />
            Bot Configuration
          </h3>
          
          <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
            <div className="sm:col-span-4">
              <label className="block text-sm font-medium text-gray-700">Telegram Bot Token</label>
              <div className="mt-1">
                <input
                  type="password"
                  value={formData.telegram_bot_token}
                  onChange={e => setFormData({...formData, telegram_bot_token: e.target.value})}
                  className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 border p-2 py-2.5 rounded-md"
                  placeholder="1234567890:ABCD..."
                />
              </div>
              <p className="mt-2 text-sm text-gray-500">Get this from @BotFather on Telegram.</p>
            </div>

            <div className="sm:col-span-4">
              <label className="block text-sm font-medium text-gray-700">Your Personal Telegram ID</label>
              <div className="mt-1">
                <input
                  type="text"
                  value={formData.telegram_id}
                  onChange={e => setFormData({...formData, telegram_id: e.target.value})}
                  className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 border p-2 py-2.5 rounded-md"
                  placeholder="e.g. 418325315"
                />
              </div>
              <p className="mt-2 text-sm text-gray-500">The bot will send alerts to this ID when it needs your help.</p>
            </div>
          </div>
          
          <div className="mt-6">
            <button
              onClick={handleSaveProfile}
              disabled={saving}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
              {ownerProfile ? 'Update Configuration' : 'Create Bot Profile'}
            </button>
          </div>
        </div>
      </div>
      
      {ownerProfile && ownerProfile.telegram_bot_token && (
        <div className="bg-primary-50 border border-primary-100 shadow sm:rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-primary-900 mb-2">
              Webhook Instructions
            </h3>
            <div className="text-sm text-primary-800 space-y-3">
              <p>Your API is ready to receive messages. To activate it, click the link below to bind Telegram to your bot:</p>
              
              <div className="bg-white p-3 rounded-md border border-primary-200 overflow-x-auto">
                <code className="text-xs break-all text-gray-800">
                  https://api.telegram.org/bot{formData.telegram_bot_token}/setWebhook?url=https://YOUR_BACKEND_RENDER_URL/webhook/telegram/{ownerProfile.id}
                </code>
              </div>
              <p className="text-xs text-primary-600 mt-1">Replace YOUR_BACKEND_RENDER_URL with your actual backend URL (e.g. replymindbot.onrender.com).</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
