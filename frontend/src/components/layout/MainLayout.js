import { useAtom } from 'jotai';
import { isAuthenticatedAtom } from '../../utils/auth';
import Link from 'next/link';
import { useRouter } from 'next/router';

export default function MainLayout({ children }) {
  const [isAuthenticated] = useAtom(isAuthenticatedAtom);
  const router = useRouter();

  // Show navigation only when authenticated
  const showNav = isAuthenticated && router.pathname !== '/';

  return (
    <div className="min-h-screen bg-gray-50">
      {showNav && (
        <nav className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <h1 className="text-xl font-semibold text-gray-900">Todo App</h1>
              </div>
              <div className="flex items-center space-x-4">
                <Link href="/dashboard" className={`px-3 py-2 rounded-md text-sm font-medium ${
                  router.pathname === '/dashboard'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}>
                  Tasks
                </Link>
              </div>
            </div>
          </div>
        </nav>
      )}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {children}
        </div>
      </main>
    </div>
  );
}