const BASE_URL = '/api';

export async function fetchHealth() {
  const res = await fetch(`${BASE_URL}/health`);
  if (!res.ok) throw new Error('Health check failed');
  return res.json();
}

export async function fetchBrands() {
  const res = await fetch(`${BASE_URL}/brands`);
  if (!res.ok) throw new Error('Failed to fetch brands');
  return res.json();
}

export async function fetchBrandDetail(brandId) {
  const res = await fetch(`${BASE_URL}/brands/${brandId}`);
  if (!res.ok) throw new Error('Failed to fetch brand details');
  return res.json();
}

export async function createBrand(brandData) {
  const res = await fetch(`${BASE_URL}/brands`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(brandData)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to create brand');
  }
  return res.json();
}

export async function addBrandRule(brandId, ruleData) {
  const res = await fetch(`${BASE_URL}/brands/${brandId}/rules`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(ruleData)
  });
  if (!res.ok) throw new Error('Failed to add brand rule');
  return res.json();
}

export async function deleteBrandRule(ruleId) {
  const res = await fetch(`${BASE_URL}/brands/rules/${ruleId}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to delete rule');
  return res.json();
}

export async function addApprovedFact(brandId, factData) {
  const res = await fetch(`${BASE_URL}/brands/${brandId}/facts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(factData)
  });
  if (!res.ok) throw new Error('Failed to add approved fact');
  return res.json();
}

export async function deleteApprovedFact(factId) {
  const res = await fetch(`${BASE_URL}/brands/facts/${factId}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to delete fact');
  return res.json();
}

export async function extractGuidelinesFromFile(file) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${BASE_URL}/brands/extract-guidelines`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) throw new Error('Failed to extract guidelines');
  return res.json();
}

export async function fetchSubmissions(brandId = null, status = null) {
  const params = new URLSearchParams();
  if (brandId) params.append('brand_id', brandId);
  if (status) params.append('status', status);
  const res = await fetch(`${BASE_URL}/submissions?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch submissions');
  return res.json();
}

export async function fetchSubmissionDetail(submissionId) {
  const res = await fetch(`${BASE_URL}/submissions/${submissionId}`);
  if (!res.ok) throw new Error('Failed to fetch submission detail');
  return res.json();
}

export async function createSubmission(formData) {
  const res = await fetch(`${BASE_URL}/submissions`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to submit content');
  }
  return res.json();
}

export async function reinspectSubmission(submissionId) {
  const res = await fetch(`${BASE_URL}/submissions/${submissionId}/reinspect`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Failed to re-inspect submission');
  return res.json();
}

export async function deleteSubmission(submissionId) {
  const res = await fetch(`${BASE_URL}/submissions/${submissionId}`, {
    method: 'DELETE'
  });
  if (!res.ok) throw new Error('Failed to delete submission');
  return res.json();
}

export async function deleteAllSubmissions(brandId = null) {
  const params = brandId ? `?brand_id=${brandId}` : '';
  const res = await fetch(`${BASE_URL}/submissions${params}`, {
    method: 'DELETE'
  });
  if (!res.ok) throw new Error('Failed to delete all submissions');
  return res.json();
}

export async function reviewFinding(findingId, reviewStatus, reviewedRevision = null, reviewerNotes = null) {
  const res = await fetch(`${BASE_URL}/review/findings/${findingId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      review_status: reviewStatus,
      reviewed_revision: reviewedRevision,
      reviewer_notes: reviewerNotes
    })
  });
  if (!res.ok) throw new Error('Failed to update finding review status');
  return res.json();
}

export async function submitFinalDecision(submissionId, decisionData) {
  const res = await fetch(`${BASE_URL}/review/submissions/${submissionId}/decision`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(decisionData)
  });
  if (!res.ok) throw new Error('Failed to submit final approval decision');
  return res.json();
}

export async function fetchBrandDrift(brandId = null) {
  const params = brandId ? `?brand_id=${brandId}` : '';
  const res = await fetch(`${BASE_URL}/analytics/brand-drift${params}`);
  if (!res.ok) throw new Error('Failed to fetch brand drift analytics');
  return res.json();
}

export async function fetchSettings() {
  const res = await fetch(`${BASE_URL}/settings`);
  if (!res.ok) throw new Error('Failed to fetch settings');
  return res.json();
}

export async function updateSettings(settingsData) {
  const res = await fetch(`${BASE_URL}/settings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settingsData)
  });
  if (!res.ok) throw new Error('Failed to update settings');
  return res.json();
}

export async function testGeminiConnection() {
  const res = await fetch(`${BASE_URL}/settings/test-gemini`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Failed to test Gemini connection');
  return res.json();
}

export async function testLocalLLMConnection() {
  const res = await fetch(`${BASE_URL}/settings/test-local-llm`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Failed to test Local LLM connection');
  return res.json();
}

export async function sendChatMessage(brandId, message, history = []) {
  const res = await fetch(`${BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      brand_id: brandId,
      message,
      history
    })
  });
  if (!res.ok) throw new Error('Failed to send chat message');
  return res.json();
}

