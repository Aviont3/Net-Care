import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AdminLayout } from '@/components/layout/AdminLayout';
import api from '@/services/api';

// ── Types ──────────────────────────────────────────────────────

interface Guardian {
  first_name: string; last_name: string; email: string;
  phone_primary: string; phone_secondary: string;
  address_street: string; address_city: string; address_state: string; address_zip: string;
  employer: string; work_phone: string; is_primary_contact: boolean;
}

interface ChildData {
  first_name: string; last_name: string; date_of_birth: string;
  gender: string; allergies: string; dietary_restrictions: string;
  medical_conditions: string; special_needs: string; enrollment_date: string;
  guardian_relationships: { guardian_index: number; relationship_type: string; is_primary: boolean; can_pickup: boolean; }[];
}

interface EmergencyContact {
  name: string; relationship_type: string; phone_primary: string;
  phone_secondary: string; priority_order: number; notes: string;
}

const BLANK_GUARDIAN: Guardian = {
  first_name: '', last_name: '', email: '', phone_primary: '', phone_secondary: '',
  address_street: '', address_city: '', address_state: 'IL', address_zip: '',
  employer: '', work_phone: '', is_primary_contact: false,
};
const BLANK_CHILD = (): ChildData => ({
  first_name: '', last_name: '', date_of_birth: '', gender: '', allergies: '',
  dietary_restrictions: '', medical_conditions: '', special_needs: '',
  enrollment_date: new Date().toISOString().split('T')[0],
  guardian_relationships: [{ guardian_index: 0, relationship_type: 'mother', is_primary: true, can_pickup: true }],
});
const BLANK_EC: EmergencyContact = {
  name: '', relationship_type: '', phone_primary: '', phone_secondary: '', priority_order: 1, notes: '',
};

const STEPS = ['Guardians', 'Children', 'Emergency Contacts', 'Review & Submit'];

// ── Sub-forms ─────────────────────────────────────────────────

function field(label: string, el: React.ReactNode, required = false) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}{required && ' *'}</label>
      {el}
    </div>
  );
}
const inp = (props: React.InputHTMLAttributes<HTMLInputElement>) => (
  <input {...props} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
);
const sel = (props: React.SelectHTMLAttributes<HTMLSelectElement>, children: React.ReactNode) => (
  <select {...props} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500">{children}</select>
);

// ── Main Wizard ────────────────────────────────────────────────

export const EnrollFamilyWizard: React.FC = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [guardians, setGuardians] = useState<Guardian[]>([{ ...BLANK_GUARDIAN, is_primary_contact: true }]);
  const [children, setChildren] = useState<ChildData[]>([BLANK_CHILD()]);
  const [emergencyContacts, setEmergencyContacts] = useState<EmergencyContact[]>([{ ...BLANK_EC, priority_order: 1 }]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  // ── Guardian helpers ──
  const setGuardian = (i: number, patch: Partial<Guardian>) =>
    setGuardians(gs => gs.map((g, idx) => idx === i ? { ...g, ...patch } : g));
  const addGuardian = () => setGuardians(gs => [...gs, { ...BLANK_GUARDIAN }]);
  const removeGuardian = (i: number) => setGuardians(gs => gs.filter((_, idx) => idx !== i));

  // ── Child helpers ──
  const setChild = (i: number, patch: Partial<ChildData>) =>
    setChildren(cs => cs.map((c, idx) => idx === i ? { ...c, ...patch } : c));
  const addChild = () => setChildren(cs => [...cs, BLANK_CHILD()]);
  const removeChild = (i: number) => setChildren(cs => cs.filter((_, idx) => idx !== i));
  const setRelationship = (ci: number, ri: number, patch: object) =>
    setChild(ci, { guardian_relationships: children[ci].guardian_relationships.map((r, idx) => idx === ri ? { ...r, ...patch } : r) });
  const addRelationship = (ci: number) =>
    setChild(ci, { guardian_relationships: [...children[ci].guardian_relationships, { guardian_index: 0, relationship_type: 'father', is_primary: false, can_pickup: true }] });

  // ── EC helpers ──
  const setEC = (i: number, patch: Partial<EmergencyContact>) =>
    setEmergencyContacts(ecs => ecs.map((e, idx) => idx === i ? { ...e, ...patch } : e));
  const addEC = () => setEmergencyContacts(ecs => [...ecs, { ...BLANK_EC, priority_order: ecs.length + 1 }]);
  const removeEC = (i: number) => setEmergencyContacts(ecs => ecs.filter((_, idx) => idx !== i));

  // ── Validation ──
  const validateStep = () => {
    if (step === 0) {
      for (const g of guardians) {
        if (!g.first_name || !g.last_name || !g.phone_primary) {
          setError('Each guardian needs a first name, last name, and primary phone.'); return false;
        }
      }
    }
    if (step === 1) {
      for (const c of children) {
        if (!c.first_name || !c.last_name || !c.date_of_birth || !c.enrollment_date) {
          setError('Each child needs a first name, last name, date of birth, and enrollment date.'); return false;
        }
      }
    }
    if (step === 2) {
      for (const ec of emergencyContacts) {
        if (!ec.name || !ec.phone_primary || !ec.relationship_type) {
          setError('Each emergency contact needs a name, relationship, and phone number.'); return false;
        }
      }
    }
    setError(''); return true;
  };

  const next = () => { if (validateStep()) setStep(s => s + 1); };
  const back = () => { setError(''); setStep(s => s - 1); };

  const submit = async () => {
    setError(''); setSubmitting(true);
    try {
      await api.post('/api/v1/enrollment/family', {
        guardians,
        children,
        emergency_contacts: emergencyContacts,
      });
      navigate('/children');
    } catch (e: any) {
      setError(e?.response?.data?.detail ?? 'Enrollment failed. Please try again.');
    } finally { setSubmitting(false); }
  };

  return (
    <AdminLayout>
      <div className="max-w-2xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Enroll a Family</h1>
          <p className="mt-1 text-gray-600">Add guardians, children, and emergency contacts in one step.</p>
        </div>

        {/* Step indicator */}
        <div className="flex items-center mb-8">
          {STEPS.map((label, i) => (
            <React.Fragment key={label}>
              <div className="flex flex-col items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-colors ${i < step ? 'bg-primary-600 text-white' : i === step ? 'bg-primary-600 text-white ring-4 ring-primary-100' : 'bg-gray-200 text-gray-500'}`}>
                  {i < step ? '✓' : i + 1}
                </div>
                <span className={`mt-1 text-xs whitespace-nowrap ${i === step ? 'text-primary-600 font-medium' : 'text-gray-400'}`}>{label}</span>
              </div>
              {i < STEPS.length - 1 && <div className={`flex-1 h-0.5 mx-2 mb-4 ${i < step ? 'bg-primary-600' : 'bg-gray-200'}`} />}
            </React.Fragment>
          ))}
        </div>

        {error && <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">{error}</div>}

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">

          {/* ── STEP 0: Guardians ── */}
          {step === 0 && (
            <div className="space-y-6">
              {guardians.map((g, i) => (
                <div key={i} className="p-4 border border-gray-200 rounded-xl">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-semibold text-gray-800">Guardian {i + 1}</h3>
                    <div className="flex items-center gap-3">
                      <label className="flex items-center gap-1.5 text-sm text-gray-600 cursor-pointer">
                        <input type="checkbox" checked={g.is_primary_contact} onChange={e => setGuardian(i, { is_primary_contact: e.target.checked })} className="rounded" />
                        Primary contact
                      </label>
                      {guardians.length > 1 && (
                        <button onClick={() => removeGuardian(i)} className="text-red-500 text-xs hover:underline">Remove</button>
                      )}
                    </div>
                  </div>
                  <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                    {field('First Name', inp({ value: g.first_name, onChange: e => setGuardian(i, { first_name: e.target.value }), placeholder: 'Sarah' }), true)}
                    {field('Last Name', inp({ value: g.last_name, onChange: e => setGuardian(i, { last_name: e.target.value }), placeholder: 'Johnson' }), true)}
                    {field('Email', inp({ type: 'email', value: g.email, onChange: e => setGuardian(i, { email: e.target.value }), placeholder: 'sarah@email.com' }))}
                    {field('Primary Phone', inp({ value: g.phone_primary, onChange: e => setGuardian(i, { phone_primary: e.target.value }), placeholder: '312-555-0123' }), true)}
                    {field('Secondary Phone', inp({ value: g.phone_secondary, onChange: e => setGuardian(i, { phone_secondary: e.target.value }) }))}
                    {field('Employer', inp({ value: g.employer, onChange: e => setGuardian(i, { employer: e.target.value }) }))}
                    {field('Street Address', inp({ value: g.address_street, onChange: e => setGuardian(i, { address_street: e.target.value }), placeholder: '123 Main St' }))}
                    {field('City', inp({ value: g.address_city, onChange: e => setGuardian(i, { address_city: e.target.value }), placeholder: 'Chicago' }))}
                    {field('State', inp({ value: g.address_state, onChange: e => setGuardian(i, { address_state: e.target.value }), maxLength: 2, placeholder: 'IL' }))}
                    {field('ZIP', inp({ value: g.address_zip, onChange: e => setGuardian(i, { address_zip: e.target.value }), placeholder: '60601' }))}
                  </div>
                </div>
              ))}
              <button onClick={addGuardian} className="text-sm text-primary-600 hover:underline font-medium">+ Add another guardian</button>
            </div>
          )}

          {/* ── STEP 1: Children ── */}
          {step === 1 && (
            <div className="space-y-6">
              {children.map((c, ci) => (
                <div key={ci} className="p-4 border border-gray-200 rounded-xl">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-semibold text-gray-800">Child {ci + 1}</h3>
                    {children.length > 1 && (
                      <button onClick={() => removeChild(ci)} className="text-red-500 text-xs hover:underline">Remove</button>
                    )}
                  </div>
                  <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                    {field('First Name', inp({ value: c.first_name, onChange: e => setChild(ci, { first_name: e.target.value }) }), true)}
                    {field('Last Name', inp({ value: c.last_name, onChange: e => setChild(ci, { last_name: e.target.value }) }), true)}
                    {field('Date of Birth', inp({ type: 'date', value: c.date_of_birth, onChange: e => setChild(ci, { date_of_birth: e.target.value }) }), true)}
                    {field('Enrollment Date', inp({ type: 'date', value: c.enrollment_date, onChange: e => setChild(ci, { enrollment_date: e.target.value }) }), true)}
                    {field('Gender', sel({ value: c.gender, onChange: e => setChild(ci, { gender: e.target.value }) },
                      <><option value="">Prefer not to say</option><option value="male">Male</option><option value="female">Female</option><option value="other">Other</option></>))}
                    {field('Allergies', inp({ value: c.allergies, onChange: e => setChild(ci, { allergies: e.target.value }), placeholder: 'Peanuts, shellfish...' }))}
                    {field('Dietary Restrictions', inp({ value: c.dietary_restrictions, onChange: e => setChild(ci, { dietary_restrictions: e.target.value }) }))}
                    {field('Medical Conditions', inp({ value: c.medical_conditions, onChange: e => setChild(ci, { medical_conditions: e.target.value }) }))}
                  </div>

                  {/* Guardian relationships */}
                  <div className="mt-4">
                    <p className="text-sm font-medium text-gray-700 mb-2">Guardian Relationships</p>
                    {c.guardian_relationships.map((rel, ri) => (
                      <div key={ri} className="flex flex-wrap gap-2 items-center mb-2 p-2 bg-gray-50 rounded-lg">
                        {sel({ value: rel.guardian_index, onChange: e => setRelationship(ci, ri, { guardian_index: Number(e.target.value) }) },
                          guardians.map((g, gi) => <option key={gi} value={gi}>{g.first_name || `Guardian ${gi + 1}`}</option>))}
                        {sel({ value: rel.relationship_type, onChange: e => setRelationship(ci, ri, { relationship_type: e.target.value }) },
                          ['mother','father','guardian','grandparent','stepmother','stepfather','aunt','uncle','other'].map(r => <option key={r} value={r}>{r}</option>))}
                        <label className="flex items-center gap-1 text-xs text-gray-600 cursor-pointer">
                          <input type="checkbox" checked={rel.is_primary} onChange={e => setRelationship(ci, ri, { is_primary: e.target.checked })} className="rounded" />
                          Primary
                        </label>
                        <label className="flex items-center gap-1 text-xs text-gray-600 cursor-pointer">
                          <input type="checkbox" checked={rel.can_pickup} onChange={e => setRelationship(ci, ri, { can_pickup: e.target.checked })} className="rounded" />
                          Can pickup
                        </label>
                      </div>
                    ))}
                    {guardians.length > c.guardian_relationships.length && (
                      <button onClick={() => addRelationship(ci)} className="text-xs text-primary-600 hover:underline">+ Add guardian link</button>
                    )}
                  </div>
                </div>
              ))}
              <button onClick={addChild} className="text-sm text-primary-600 hover:underline font-medium">+ Add another child</button>
            </div>
          )}

          {/* ── STEP 2: Emergency Contacts ── */}
          {step === 2 && (
            <div className="space-y-4">
              <p className="text-sm text-gray-500">DCFS requires at least 2 emergency contacts. These will be linked to all enrolled children.</p>
              {emergencyContacts.map((ec, i) => (
                <div key={i} className="p-4 border border-gray-200 rounded-xl">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-semibold text-gray-800">Contact #{ec.priority_order}</h3>
                    {emergencyContacts.length > 1 && (
                      <button onClick={() => removeEC(i)} className="text-red-500 text-xs hover:underline">Remove</button>
                    )}
                  </div>
                  <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                    {field('Full Name', inp({ value: ec.name, onChange: e => setEC(i, { name: e.target.value }), placeholder: 'Jane Smith' }), true)}
                    {field('Relationship', inp({ value: ec.relationship_type, onChange: e => setEC(i, { relationship_type: e.target.value }), placeholder: 'Grandmother, Aunt...' }), true)}
                    {field('Primary Phone', inp({ value: ec.phone_primary, onChange: e => setEC(i, { phone_primary: e.target.value }), placeholder: '312-555-0000' }), true)}
                    {field('Secondary Phone', inp({ value: ec.phone_secondary, onChange: e => setEC(i, { phone_secondary: e.target.value }) }))}
                    {field('Notes', inp({ value: ec.notes, onChange: e => setEC(i, { notes: e.target.value }), placeholder: 'Call only after 5pm...' }))}
                  </div>
                </div>
              ))}
              <button onClick={addEC} className="text-sm text-primary-600 hover:underline font-medium">+ Add emergency contact</button>
            </div>
          )}

          {/* ── STEP 3: Review ── */}
          {step === 3 && (
            <div className="space-y-5 text-sm">
              <div>
                <h3 className="font-semibold text-gray-800 mb-2">Guardians ({guardians.length})</h3>
                {guardians.map((g, i) => (
                  <div key={i} className="px-3 py-2 bg-gray-50 rounded-lg mb-1.5">
                    <span className="font-medium">{g.first_name} {g.last_name}</span>
                    {g.email && <span className="text-gray-500 ml-2">{g.email}</span>}
                    <span className="text-gray-500 ml-2">{g.phone_primary}</span>
                    {g.is_primary_contact && <span className="ml-2 text-xs bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded">Primary</span>}
                  </div>
                ))}
              </div>
              <div>
                <h3 className="font-semibold text-gray-800 mb-2">Children ({children.length})</h3>
                {children.map((c, i) => (
                  <div key={i} className="px-3 py-2 bg-gray-50 rounded-lg mb-1.5">
                    <span className="font-medium">{c.first_name} {c.last_name}</span>
                    <span className="text-gray-500 ml-2">DOB: {c.date_of_birth}</span>
                    <span className="text-gray-500 ml-2">Enrolls: {c.enrollment_date}</span>
                    {c.allergies && <span className="ml-2 text-xs bg-red-100 text-red-700 px-1.5 py-0.5 rounded">⚠ {c.allergies}</span>}
                  </div>
                ))}
              </div>
              <div>
                <h3 className="font-semibold text-gray-800 mb-2">Emergency Contacts ({emergencyContacts.length})</h3>
                {emergencyContacts.map((ec, i) => (
                  <div key={i} className="px-3 py-2 bg-gray-50 rounded-lg mb-1.5">
                    <span className="font-medium">{ec.name}</span>
                    <span className="text-gray-500 ml-2">({ec.relationship_type})</span>
                    <span className="text-gray-500 ml-2">{ec.phone_primary}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Navigation */}
        <div className="flex justify-between mt-6">
          <button onClick={back} disabled={step === 0}
            className="px-5 py-2 border border-gray-300 text-sm font-medium rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-40 transition-colors">
            ← Back
          </button>
          {step < 3 ? (
            <button onClick={next}
              className="px-6 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors">
              Next →
            </button>
          ) : (
            <button onClick={submit} disabled={submitting}
              className="px-6 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors">
              {submitting ? 'Enrolling...' : '✓ Enroll Family'}
            </button>
          )}
        </div>
      </div>
    </AdminLayout>
  );
};
