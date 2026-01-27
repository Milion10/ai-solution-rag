/**
 * Configuration API centralisée
 * Utilise NEXT_PUBLIC_API_URL depuis .env
 */

/**
 * URL de base de l'API backend
 * En développement: http://localhost:8000
 * En production: Doit être configuré via NEXT_PUBLIC_API_URL
 */
export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Validation de la configuration au build
 * Force la définition de NEXT_PUBLIC_API_URL en production
 */
if (typeof window === 'undefined') {
  // Code côté serveur (build time)
  if (process.env.NODE_ENV === 'production' && !process.env.NEXT_PUBLIC_API_URL) {
    console.error(
      '🔴 ERREUR: NEXT_PUBLIC_API_URL doit être défini en production !\n' +
      '   Ajoutez NEXT_PUBLIC_API_URL=https://votre-api.com dans .env.production'
    );
    // Ne pas throw en production pour éviter de casser le build
    // mais logger l'erreur clairement
  }
}

/**
 * Helper pour construire une URL d'API
 * @param endpoint - Endpoint de l'API (ex: '/api/chat')
 * @returns URL complète
 */
export function getApiUrl(endpoint: string): string {
  // Retirer le slash initial si présent pour éviter doubles slashes
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${API_URL}${cleanEndpoint}`;
}

/**
 * Configuration fetch avec gestion d'erreurs
 * @param endpoint - Endpoint de l'API
 * @param options - Options fetch standard
 * @returns Promise<Response>
 */
export async function fetchAPI(
  endpoint: string,
  options?: RequestInit
): Promise<Response> {
  const url = getApiUrl(endpoint);
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });
    
    return response;
  } catch (error) {
    console.error(`Erreur lors de la requête vers ${url}:`, error);
    throw error;
  }
}

// Log configuration au démarrage (côté client uniquement)
if (typeof window !== 'undefined') {
  console.log('🌐 API Backend:', API_URL);
}
