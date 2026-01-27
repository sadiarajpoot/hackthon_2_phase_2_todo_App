import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAtom } from 'jotai';
import { isAuthenticatedAtom } from '../../utils/auth';
import api from '../../services/api';
import authService from '../../services/auth';
import { PlusIcon, CheckIcon, TrashIcon, PencilIcon, CalendarIcon, ClockIcon, CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline';
import { CheckCircleIcon as CheckCircleSolidIcon } from '@heroicons/react/24/solid';

export default function Dashboard() {
  const [tasks, setTasks] = useState([]);
  const [newTask, setNewTask] = useState({ title: '', description: '' });
  const [editingTask, setEditingTask] = useState(null); // Track which task is being edited
  const [editingTaskData, setEditingTaskData] = useState({ title: '', description: '' }); // Editing form data
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useAtom(isAuthenticatedAtom);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState('success'); // 'success' or 'error'
  const router = useRouter();

  useEffect(() => {
    // Check authentication status
    const token = localStorage.getItem('access_token');
    if (!token) {
      setIsAuthenticated(false);
      router.push('/login');
      return;
    }

    fetchTasks();
  }, [router, setIsAuthenticated]);

  const showToastMessage = (message, type = 'success') => {
    setToastMessage(message);
    setToastType(type);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const tasksData = await api.getTasks();
      setTasks(tasksData);
      setError('');
    } catch (err) {
      setError(err.message || 'Failed to load tasks');
      showToastMessage(err.message || 'Failed to load tasks', 'error');
      // If unauthorized, redirect to login
      if (err.message.includes('401') || err.message.includes('403')) {
        authService.logout();
        setIsAuthenticated(false);
        router.push('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleEditTask = (task) => {
    setEditingTask(task.id);
    setEditingTaskData({ title: task.title, description: task.description || '' });
  };

  const handleCancelEdit = () => {
    setEditingTask(null);
    setEditingTaskData({ title: '', description: '' });
  };

  const handleSaveEdit = async (taskId) => {
    if (!editingTaskData.title.trim()) {
      showToastMessage('Task title is required', 'error');
      return;
    }

    try {
      const updatedTask = await api.updateTask(taskId, editingTaskData);
      setTasks(tasks.map(task =>
        task.id === taskId ? updatedTask : task
      ));
      setEditingTask(null);
      setEditingTaskData({ title: '', description: '' });
      showToastMessage('Task updated successfully!');
    } catch (err) {
      setError(err.message || 'Failed to update task');
      showToastMessage(err.message || 'Failed to update task', 'error');
    }
  };

  const handleCreateTask = async (e) => {
    e.preventDefault();
    if (!newTask.title.trim()) return;

    try {
      const createdTask = await api.createTask(newTask);
      setTasks([...tasks, createdTask]);
      setNewTask({ title: '', description: '' });
      setError('');
      showToastMessage('Task created successfully!');
    } catch (err) {
      setError(err.message || 'Failed to create task');
      showToastMessage(err.message || 'Failed to create task', 'error');
    }
  };

  const handleToggleTask = async (taskId) => {
    try {
      const updatedTask = await api.toggleTaskCompletion(taskId);
      setTasks(tasks.map(task =>
        task.id === taskId ? { ...task, is_completed: updatedTask.is_completed, updated_at: updatedTask.updated_at } : task
      ));
      setError('');
      showToastMessage(updatedTask.is_completed ? 'Task completed!' : 'Task marked as incomplete');
    } catch (err) {
      setError(err.message || 'Failed to update task');
      showToastMessage(err.message || 'Failed to update task', 'error');
    }
  };

  const handleDeleteTask = async (taskId) => {
    if (!window.confirm('Are you sure you want to delete this task? This action cannot be undone.')) return;

    try {
      await api.deleteTask(taskId);
      setTasks(tasks.filter(task => task.id !== taskId));
      setError('');
      showToastMessage('Task deleted successfully!');
    } catch (err) {
      setError(err.message || 'Failed to delete task');
      showToastMessage(err.message || 'Failed to delete task', 'error');
    }
  };

  const handleLogout = async () => {
    try {
      await authService.logout();
      setIsAuthenticated(false);
      router.push('/login');
    } catch (err) {
      setError(err.message || 'Logout failed');
      showToastMessage(err.message || 'Logout failed', 'error');
    }
  };

  if (!isAuthenticated) {
    return null; // Redirect will happen in useEffect
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Toast Notification */}
      {showToast && (
        <div className={`fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transform transition-all duration-300 ${
          toastType === 'success'
            ? 'bg-green-500 text-white'
            : 'bg-red-500 text-white'
        }`}>
          <div className="flex items-center">
            {toastType === 'success' ? (
              <CheckCircleIcon className="w-5 h-5 mr-2" />
            ) : (
              <XCircleIcon className="w-5 h-5 mr-2" />
            )}
            <span>{toastMessage}</span>
          </div>
        </div>
      )}

      <nav className="bg-white/80 backdrop-blur-sm border-b border-slate-200/50 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0 flex items-center">
                <div className="h-8 w-8 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 flex items-center justify-center">
                  <CheckIcon className="h-5 w-5 text-white" />
                </div>
                <span className="ml-2 text-xl font-bold bg-gradient-to-r from-slate-800 to-slate-600 bg-clip-text text-transparent">
                  TaskFlow
                </span>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={handleLogout}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-r from-rose-500 to-rose-600 hover:from-rose-600 hover:to-rose-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-rose-500 transition-all duration-200 hover:shadow-md"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8 text-center">
          <h1 className="text-3xl md:text-4xl font-bold text-slate-800 mb-2">
            Your Task Dashboard
          </h1>
          <p className="text-slate-600">Manage your tasks efficiently and stay productive</p>
        </div>

        {/* Create Task Form */}
        <div className="mb-12">
          <div className="max-w-2xl mx-auto">
            <div className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-lg border border-slate-200/50 p-6 md:p-8 transition-all duration-300 hover:shadow-xl">
              <h2 className="text-xl font-semibold text-slate-800 mb-6 text-center">Create New Task</h2>

              {error && (
                <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <XCircleIcon className="h-5 w-5 text-red-400" />
                    </div>
                    <div className="ml-3">
                      <p className="text-sm text-red-700">{error}</p>
                    </div>
                  </div>
                </div>
              )}

              <form onSubmit={handleCreateTask} className="space-y-6">
                <div>
                  <label htmlFor="title" className="block text-sm font-medium text-slate-700 mb-2">
                    Task Title *
                  </label>
                  <input
                    type="text"
                    id="title"
                    value={newTask.title}
                    onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
                    className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 bg-white/80 backdrop-blur-sm"
                    placeholder="What needs to be done?"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="description" className="block text-sm font-medium text-slate-700 mb-2">
                    Description
                  </label>
                  <textarea
                    id="description"
                    value={newTask.description}
                    onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
                    className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 bg-white/80 backdrop-blur-sm min-h-[100px]"
                    placeholder="Add details about your task (optional)"
                  />
                </div>

                <button
                  type="submit"
                  className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-3 px-6 rounded-lg font-medium hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all duration-200 hover:shadow-lg flex items-center justify-center"
                >
                  <PlusIcon className="w-5 h-5 mr-2" />
                  Create Task
                </button>
              </form>
            </div>
          </div>
        </div>

        {/* Tasks Section */}
        <div>
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-2xl font-semibold text-slate-800">Your Tasks</h2>
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-slate-100 text-slate-800">
              {tasks.length} {tasks.length === 1 ? 'task' : 'tasks'}
            </span>
          </div>

          {loading ? (
            <div className="text-center py-16">
              <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-b-4 border-indigo-600 mx-auto mb-4"></div>
              <p className="text-slate-600 text-lg">Loading your tasks...</p>
            </div>
          ) : tasks.length === 0 ? (
            <div className="text-center py-16">
              <div className="mx-auto w-32 h-32 bg-gradient-to-br from-slate-200 to-slate-300 rounded-full flex items-center justify-center mb-6">
                <CheckCircleIcon className="w-16 h-16 text-slate-400" />
              </div>
              <h3 className="text-xl font-semibold text-slate-800 mb-2">No tasks yet</h3>
              <p className="text-slate-600 mb-6">Create your first task to get started on your productivity journey</p>
              <div className="animate-pulse">
                <div className="h-2 bg-slate-200 rounded w-3/4 mx-auto mb-2"></div>
                <div className="h-2 bg-slate-200 rounded w-1/2 mx-auto"></div>
              </div>
            </div>
          ) : (
            <div className="grid gap-4 md:gap-6 max-w-4xl mx-auto">
              {tasks.map((task, index) => (
                <div
                  key={task.id}
                  className={`bg-white/70 backdrop-blur-sm rounded-xl shadow-md border border-slate-200/50 p-6 transition-all duration-300 hover:shadow-lg hover:border-slate-300/50 ${
                    task.is_completed
                      ? 'bg-gradient-to-r from-emerald-50/70 to-emerald-100/70 border-l-4 border-l-emerald-500'
                      : 'bg-white/70'
                  }`}
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  {editingTask === task.id ? (
                    // Edit form
                    <div className="space-y-4">
                      <div>
                        <label htmlFor={`edit-title-${task.id}`} className="block text-sm font-medium text-slate-700 mb-2">
                          Task Title *
                        </label>
                        <input
                          id={`edit-title-${task.id}`}
                          type="text"
                          value={editingTaskData.title}
                          onChange={(e) => setEditingTaskData({ ...editingTaskData, title: e.target.value })}
                          className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 bg-white/80 backdrop-blur-sm"
                          placeholder="What needs to be done?"
                          required
                        />
                      </div>

                      <div>
                        <label htmlFor={`edit-desc-${task.id}`} className="block text-sm font-medium text-slate-700 mb-2">
                          Description
                        </label>
                        <textarea
                          id={`edit-desc-${task.id}`}
                          value={editingTaskData.description}
                          onChange={(e) => setEditingTaskData({ ...editingTaskData, description: e.target.value })}
                          className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 bg-white/80 backdrop-blur-sm min-h-[100px]"
                          placeholder="Add details about your task (optional)"
                        />
                      </div>

                      <div className="flex space-x-3">
                        <button
                          onClick={() => handleSaveEdit(task.id)}
                          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-700 hover:to-emerald-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 transition-all duration-200 hover:shadow-md"
                        >
                          <CheckIcon className="w-4 h-4 mr-1" />
                          Save
                        </button>
                        <button
                          onClick={handleCancelEdit}
                          className="inline-flex items-center px-4 py-2 border border-slate-300 text-sm font-medium rounded-lg text-slate-700 bg-white hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-500 transition-all duration-200"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    // Display task view
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-4 flex-1">
                        <button
                          onClick={() => handleToggleTask(task.id)}
                          className={`mt-1 h-6 w-6 rounded-full border-2 flex items-center justify-center transition-all duration-200 ${
                            task.is_completed
                              ? 'bg-emerald-500 border-emerald-500 text-white shadow-sm'
                              : 'border-slate-300 hover:border-indigo-500 hover:scale-110'
                          }`}
                        >
                          {task.is_completed && (
                            <CheckIcon className="h-4 w-4" />
                          )}
                        </button>
                        <div className="flex-1 min-w-0">
                          <h3
                            className={`text-lg font-medium mb-2 transition-all duration-200 ${
                              task.is_completed
                                ? 'text-slate-500 line-through'
                                : 'text-slate-800'
                            }`}
                          >
                            {task.title}
                          </h3>
                          {task.description && (
                            <p className={`text-slate-600 mb-3 ${task.is_completed ? 'text-slate-400' : 'text-slate-600'}`}>
                              {task.description}
                            </p>
                          )}
                          <div className="flex items-center text-sm text-slate-500 space-x-4">
                            <span className="flex items-center">
                              <CalendarIcon className="w-4 h-4 mr-1" />
                              Created: {new Date(task.created_at).toLocaleDateString()}
                            </span>
                            {task.updated_at !== task.created_at && (
                              <span className="flex items-center">
                                <ClockIcon className="w-4 h-4 mr-1" />
                                Updated: {new Date(task.updated_at).toLocaleDateString()}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleEditTask(task)}
                          className="p-2 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-full transition-all duration-200 hover:scale-110"
                          title="Edit task"
                        >
                          <PencilIcon className="w-5 h-5" />
                        </button>
                        <button
                          onClick={() => handleDeleteTask(task.id)}
                          className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-full transition-all duration-200 hover:scale-110"
                          title="Delete task"
                        >
                          <TrashIcon className="w-5 h-5" />
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Floating Action Button for Mobile */}
      <button
        onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
        className="fixed bottom-6 right-6 md:hidden p-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-200 hover:scale-110 z-30"
        title="Back to top"
      >
        <PencilIcon className="w-6 h-6" />
      </button>
    </div>
  );
}