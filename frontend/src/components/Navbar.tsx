import { Link } from 'react-router-dom';
import { useAuth, supabase } from '../contexts/AuthContext';
import { LogOut, LayoutDashboard, BrainCircuit } from 'lucide-react';

export default function Navbar() {
  const { user } = useAuth();

  const handleSignOut = async () => {
    await supabase.auth.signOut();
  };

  if (!user) return null;

  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <Link to="/dashboard" className="flex items-center gap-2">
                <BrainCircuit className="h-8 w-8 text-primary-600" />
                <span className="font-bold text-xl text-gray-900">ReplyMind</span>
              </Link>
            </div>
            <div className="hidden sm:-my-px sm:ml-6 sm:flex sm:space-x-8">
              <Link
                to="/dashboard"
                className="border-primary-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
              >
                <LayoutDashboard className="h-4 w-4 mr-2" />
                Dashboard
              </Link>
            </div>
          </div>
          <div className="flex items-center">
            <button
              onClick={handleSignOut}
              className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-gray-500 hover:text-gray-700 bg-white hover:bg-gray-50 focus:outline-none transition ease-in-out duration-150"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Sign out
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
