export function missingDocuments(claim) {
  return claim.requiredDocuments.filter(name => !claim.receivedDocuments.includes(name));
}

export function statusOf(claim) {
  if (claim.owner) return 'Assigned';
  return missingDocuments(claim).length ? 'Awaiting documents' : 'Unassigned';
}

export function filterClaims(claims, status) {
  return status === 'All claims' ? claims : claims.filter(claim => statusOf(claim) === status);
}

export function filedTime(claim) {
  return new Intl.DateTimeFormat('en-GB', {
    timeZone: 'Asia/Kolkata', hour: '2-digit', minute: '2-digit',
  }).format(new Date(claim.filedAt));
}
