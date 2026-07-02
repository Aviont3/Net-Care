
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);

import { childrenService } from '@/services/childrenService';
import { activityService, type Activity, type ActivityCreate } from '@/services/activityService';
import type { Child } from '@/types';

const ACTIVITY_TYPES = ['meal', 'nap', 'diaper', 'play', 'learning', 'outdoor'] as const;
const MOODS = ['happy', 'sad', 'energetic', 'tired', 'cranky', 'neutral'] as const;

const TYPE_LABELS: Record<string, string> = {
  meal: '🍽 Meal', nap: '😴 Nap', diaper: '🧷 Diaper',
  play: '🎮 Play', learning: '📚 Learning', outdoor: '🌳 Outdoor',
};
const MOOD_LABELS: Record<string, string> = {
  happy: '😊 Happy', sad: '😢 Sad', energetic: '⚡ Energetic',
  tired: '😴 Tired', cranky: '😤 Cranky', neutral: '😐 Neutral',
};
const TYPE_COLORS: Record<string, string> = {
  meal: 'bg-orange-100 text-orange-700',
  nap: 'bg-indigo-100 text-indigo-700',
  diaper: 'bg-pink-100 text-pink-700',
  play: 'bg-green-100 text-green-700',
  learning: 'bg-blue-100 text-blue-700',
  outdoor: 'bg-teal-100 text-teal-700',
};

const MEAL_TYPES = ['breakfast', 'lunch', 'supper', 'snack'] as const;
const MEAL_TYPE_LABELS: Record<string, string> = {
  breakfast: '🌅 Breakfast',
  lunch: '☀️ Lunch',
  supper: '🌙 Supper',
  snack: '🍎 Snack',
};

// Food component keys expected by the CACFP validator
const FOOD_COMPONENT_KEYS = ['milk', 'grains', 'fruit', 'vegetable', 'meat_alternate'] as const;
type FoodComponentKey = typeof FOOD_COMPONENT_KEYS[number];

const FOOD_COMPONENT_LABELS: Record<FoodComponentKey, string> = {
  milk:          '🥛 Milk',
  grains:        '🌾 Grains',
  fruit:         '🍎 Fruit',
  vegetable:     '🥦 Vegetable',
  meat_alternate:'🍗 Meat / Alternate',
};

type FoodComponents = Record<FoodComponentKey, string>;

const EMPTY_FOOD_COMPONENTS: FoodComponents = {
  milk: '', grains: '', fruit: '', vegetable: '', meat_alternate: '',
};

const EMPTY_FORM: ActivityCreate = {
  child_id: '', activity_type: 'meal', meal_type: '', activity_name: '',
  description: '', mood: '', duration_minutes: undefined, notes: '',
};

export const ActivitiesPage: React.FC = () => {
  const [children, setChildren] = useState<Child[]>([]);
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [form, setForm] = useState<ActivityCreate>(EMPTY_FORM);
  const [foodComponents, setFoodComponents] = useState<FoodComponents>(EMPTY_FOOD_COMPONENTS);
  const [lastCompliance, setLastCompliance] = useState<{ compliant: boolean; notes: string } | null>(null);
  const [filterType, setFilterType] = useState('');
  const [filterChild, setFilterChild] = useState('');

  // Map child_id -> name for display
  const childName = (id: string) => {
    const c = children.find(ch => ch.id === id);
    return c ? `${c.first_name} ${c.last_name}` : '—';
  };

  const fetchActivities = async () => {
    try {
      const data = await activityService.getTodayActivities({
        ...(filterChild && { child_id: filterChild }),
        ...(filterType && { activity_type: filterType }),
      });
      setActivities(data);
    } catch {
      // non-critical, keep existing list
    }
  };

  useEffect(() => {
    const init = async () => {
      try {
        const [childRes, actRes] = await Promise.all([
          childrenService.getChildren({ is_active: true, page_size: 200 }),
          activityService.getTodayActivities(),
        ]);
        setChildren(childRes.children);
        setActivities(actRes);
      } catch {
        setError('Failed to load data.');
      } finally {
        setLoading(false);
      }
    };
    init();
  }, []);

  // Re-fetch when filters change
  useEffect(() => {
    if (!loading) fetchActivities();
  }, [filterType, filterChild]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setForm(f => {
      const updated = { ...f, [name]: name === 'duration_minutes' ? (value ? Number(value) : undefined) : value };
      // Clear meal_type + food components when switching away from "meal" activity type
      if (name === 'activity_type' && value !== 'meal') {
        updated.meal_type = '';
      }
      return updated;
    });
    // Reset food components and compliance state when activity type or meal type changes
    if (name === 'activity_type' && value !== 'meal') {
      setFoodComponents(EMPTY_FOOD_COMPONENTS);
      setLastCompliance(null);
    }
    if (name === 'meal_type') {
      setFoodComponents(EMPTY_FOOD_COMPONENTS);
      setLastCompliance(null);
    }
  };

  const handleFoodComponentChange = (key: FoodComponentKey, value: string) => {
    setFoodComponents(prev => ({ ...prev, [key]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.child_id) { setError('Please select a child.'); return; }
    if (!form.activity_name.trim()) { setError('Activity name is required.'); return; }
    setError('');
    setSubmitting(true);
    try {
      // Build food_components: only include keys with a non-empty value
      const hasComponents = form.activity_type === 'meal' && form.meal_type;
      const builtComponents = hasComponents
        ? Object.fromEntries(
            FOOD_COMPONENT_KEYS.map(k => [k, foodComponents[k] || null])
          )
        : undefined;

      const payload: ActivityCreate = {
        ...form,
        meal_type: form.meal_type || undefined,
        mood: form.mood || undefined,
        description: form.description || undefined,
        notes: form.notes || undefined,
        food_components: builtComponents,
      };
      const created = await activityService.createActivity(payload);

      // Surface compliance result from the API response
      if (created.cacfp_compliant !== undefined && created.cacfp_compliant !== null) {
        setLastCompliance({
          compliant: created.cacfp_compliant,
          notes: created.compliance_notes ?? '',
        });
      } else {
        setLastCompliance(null);
      }

      // Upload photo if one was selected
      if (photoFile && created.id) {
        try {
          await activityService.uploadPhoto(created.id, photoFile);
        } catch {
          // Activity was created but photo upload failed — non-blocking
          console.warn('Photo upload failed');
        }
      }

      setSuccess('Activity logged successfully!');
      setForm(EMPTY_FORM);
      setFoodComponents(EMPTY_FOOD_COMPONENTS);
      setPhotoFile(null);
      setPhotoPreview(null);
      await fetchActivities();
      setTimeout(() => setSuccess(''), 3000);
    } catch {
      setError('Failed to log activity. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const formatTime = (iso: string) => {
    try { return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }); }
    catch { return iso; }
  };

  return (
    <AdminLayout>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Daily Activities</h1>
        <p className="mt-1 text-gray-600">Log meals, naps, diaper changes, and play for today.</p>
      </div>

      {/* Log Activity Form */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Log Activity</h2>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">{error}</div>
        )}
        {success && (
          <div className="mb-4 p-3 bg-green-50 border border-green-200 text-green-700 rounded-lg text-sm">{success}</div>
        )}

        <form onSubmit={handleSubmit} className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {/* Child */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Child *</label>
            <select name="child_id" value={form.child_id} onChange={handleChange}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500">
              <option value="">Select child...</option>
              {children.map(c => (
                <option key={c.id} value={c.id}>{c.first_name} {c.last_name}</option>
              ))}
            </select>
          </div>

          {/* Activity Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Activity Type *</label>
            <select name="activity_type" value={form.activity_type} onChange={handleChange}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500">
              {ACTIVITY_TYPES.map(t => (
                <option key={t} value={t}>{TYPE_LABELS[t]}</option>
              ))}
            </select>
          </div>

          {/* Meal Type — only shown when activity_type is "meal" */}
          {form.activity_type === 'meal' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Meal Type</label>
              <select name="meal_type" value={form.meal_type ?? ''} onChange={handleChange}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500">
                <option value="">Not specified</option>
                {MEAL_TYPES.map(m => (
                  <option key={m} value={m}>{MEAL_TYPE_LABELS[m]}</option>
                ))}
              </select>
            </div>
          )}

          {/* Food Components — shown when meal type is selected (CACFP tracking) */}
          {form.activity_type === 'meal' && form.meal_type && (
            <div className="sm:col-span-2 lg:col-span-3">
              <div className="border border-orange-200 rounded-lg p-4 bg-orange-50">
                <h3 className="text-sm font-semibold text-orange-800 mb-3">
                  🥗 CACFP Food Components
                  <span className="ml-2 text-xs font-normal text-orange-600">
                    Check the box and describe what was served for USDA reimbursement tracking
                  </span>
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {FOOD_COMPONENT_KEYS.map(key => (
                    <div key={key} className="flex items-start gap-2">
                      <input
                        type="checkbox"
                        id={`fc_${key}`}
                        checked={!!foodComponents[key]}
                        onChange={e => handleFoodComponentChange(key, e.target.checked ? ' ' : '')}
                        className="mt-2.5 h-4 w-4 rounded border-gray-300 text-orange-600 focus:ring-orange-500 shrink-0"
                      />
                      <div className="flex-1 min-w-0">
                        <label htmlFor={`fc_${key}`} className="block text-xs font-medium text-gray-700 mb-1 cursor-pointer">
                          {FOOD_COMPONENT_LABELS[key]}
                        </label>
                        <input
                          type="text"
                          value={foodComponents[key]}
                          onChange={e => handleFoodComponentChange(key, e.target.value)}
                          placeholder={key === 'milk' ? 'e.g. Whole milk' : key === 'grains' ? 'e.g. Whole wheat bread' : key === 'fruit' ? 'e.g. Apple slices' : key === 'vegetable' ? 'e.g. Carrots' : 'e.g. Chicken'}
                          className="w-full border border-gray-300 rounded px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-orange-400 disabled:bg-gray-50 disabled:text-gray-400"
                          disabled={!foodComponents[key] && foodComponents[key] !== ' '}
                        />
                      </div>
                    </div>
                  ))}
                </div>

                {/* Inline compliance badge — shown after last submission */}
                {lastCompliance !== null && (
                  <div className={`mt-3 flex items-start gap-2 p-2.5 rounded-lg text-xs font-medium ${
                    lastCompliance.compliant
                      ? 'bg-green-100 text-green-800 border border-green-200'
                      : 'bg-red-100 text-red-800 border border-red-200'
                  }`}>
                    <span className="text-base leading-none shrink-0">
                      {lastCompliance.compliant ? '✅' : '❌'}
                    </span>
                    <span>
                      {lastCompliance.compliant
                        ? 'CACFP compliant — all required components present.'
                        : `Not CACFP compliant: ${lastCompliance.notes}`}
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Activity Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Activity Name *</label>
            <input type="text" name="activity_name" value={form.activity_name} onChange={handleChange}
              placeholder="e.g. Lunch, Afternoon nap..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
          </div>

          {/* Mood */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Mood</label>
            <select name="mood" value={form.mood} onChange={handleChange}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500">
              <option value="">Not specified</option>
              {MOODS.map(m => (
                <option key={m} value={m}>{MOOD_LABELS[m]}</option>
              ))}
            </select>
          </div>

          {/* Duration */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Duration (minutes)</label>
            <input type="number" name="duration_minutes" value={form.duration_minutes ?? ''} onChange={handleChange}
              min={1} placeholder="Optional"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <input type="text" name="description" value={form.description} onChange={handleChange}
              placeholder="Optional details..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
          </div>

          {/* Notes — full width */}
          <div className="sm:col-span-2 lg:col-span-3">
            <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
            <textarea name="notes" value={form.notes} onChange={handleChange}
              rows={2} placeholder="Any additional notes..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none" />
          </div>

          {/* Photo Attachment */}
          <div className="sm:col-span-2 lg:col-span-3">
            <label className="block text-sm font-medium text-gray-700 mb-1">Photo (optional)</label>
            <div className="flex items-center gap-3">
              <label className="cursor-pointer inline-flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm text-gray-700 transition-colors">
                <svg className="w-5 h-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                {photoFile ? 'Change Photo' : 'Add Photo'}
                <input type="file" accept="image/*" capture="environment" className="hidden"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) {
                      setPhotoFile(file);
                      setPhotoPreview(URL.createObjectURL(file));
                    }
                  }} />
              </label>
              {photoPreview && (
                <div className="relative">
                  <img src={photoPreview} alt="Preview" className="w-16 h-16 object-cover rounded-lg border" />
                  <button type="button" onClick={() => { setPhotoFile(null); setPhotoPreview(null); }}
                    className="absolute -top-1.5 -right-1.5 w-5 h-5 bg-red-500 text-white rounded-full text-xs flex items-center justify-center">×</button>
                </div>
              )}
            </div>
          </div>

          <div className="sm:col-span-2 lg:col-span-3 flex justify-end">
            <button type="submit" disabled={submitting}
              className="px-6 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors">
              {submitting ? 'Logging...' : 'Log Activity'}
            </button>
          </div>
        </form>
      </div>

      {/* Today's Activity Feed */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="px-6 py-4 border-b border-gray-100 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <h2 className="text-lg font-semibold text-gray-900">
            Today's Activities
            <span className="ml-2 text-sm font-normal text-gray-500">({activities.length})</span>
          </h2>
          <div className="flex gap-2">
            <select value={filterChild} onChange={e => setFilterChild(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500">
              <option value="">All children</option>
              {children.map(c => (
                <option key={c.id} value={c.id}>{c.first_name} {c.last_name}</option>
              ))}
            </select>
            <select value={filterType} onChange={e => setFilterType(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500">
              <option value="">All types</option>
              {ACTIVITY_TYPES.map(t => (
                <option key={t} value={t}>{TYPE_LABELS[t]}</option>
              ))}
            </select>
          </div>
        </div>

        {loading ? (
          <div className="p-12 text-center text-gray-500">Loading...</div>
        ) : activities.length === 0 ? (
          <div className="p-12 text-center text-gray-500">No activities logged today yet.</div>
        ) : (
          <ul className="divide-y divide-gray-100">
            {activities.map(a => (
              <li key={a.id} className="px-6 py-4 flex items-start gap-4">
                <span className={`shrink-0 px-2.5 py-1 rounded-full text-xs font-medium ${TYPE_COLORS[a.activity_type] ?? 'bg-gray-100 text-gray-700'}`}>
                  {TYPE_LABELS[a.activity_type] ?? a.activity_type}
                </span>
                <div className="flex-1 min-w-0">
                  <div className="flex flex-wrap items-baseline gap-x-2">
                    <span className="font-medium text-gray-900 text-sm">{a.activity_name}</span>
                    <span className="text-xs text-gray-500">{childName(a.child_id)}</span>
                    {/* CACFP compliance badge */}
                    {a.activity_type === 'meal' && a.cacfp_compliant !== undefined && a.cacfp_compliant !== null && (
                      <span
                        title={a.cacfp_compliant ? 'CACFP compliant' : (a.compliance_notes ?? 'Not CACFP compliant')}
                        className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-xs font-medium ${
                          a.cacfp_compliant
                            ? 'bg-green-100 text-green-700'
                            : 'bg-red-100 text-red-700'
                        }`}>
                        {a.cacfp_compliant ? '✓ CACFP' : '✗ CACFP'}
                      </span>
                    )}
                  </div>
                  {a.description && <p className="text-sm text-gray-600 mt-0.5">{a.description}</p>}
                  {a.notes && <p className="text-xs text-gray-500 mt-0.5 italic">{a.notes}</p>}
                  {a.photo_url && (
                    <img src={a.photo_url} alt="Activity photo" className="mt-2 w-32 h-24 object-cover rounded-lg border border-gray-200 shadow-sm" />
                  )}
                  <div className="flex flex-wrap gap-x-3 mt-1 text-xs text-gray-400">
                    <span>{formatTime(a.activity_time)}</span>
                    {a.duration_minutes && <span>{a.duration_minutes} min</span>}
                    {a.mood && <span>{MOOD_LABELS[a.mood] ?? a.mood}</span>}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </AdminLayout>
  );
};
