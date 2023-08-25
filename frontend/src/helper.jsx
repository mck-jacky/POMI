const serverURL = 'http://localhost:5001/'

export async function fetchURL (API, method, body = {}) {
  const options = {
    method,
    headers: {
      'Content-type': 'application/json'
    }
  }

  if (method !== 'GET') {
    options.body = JSON.stringify(body);
  }

  let res = await fetch(serverURL + API, options);
  res = await res.json();
  return res
}

export async function fetchGetURL(API, params = {}) {
  const url = new URL(serverURL + API);

  Object.keys(params).forEach((key) =>
    url.searchParams.append(key, params[key])
  );

  const options = {
    method: 'GET',
    headers: {
      'Content-type': 'application/json',
    },
  };

  const response = await fetch(url.toString(), options);
  const data = await response.json();
  return data;
}


export const isLogin = (userObj) => {
  if (userObj && userObj.user) {
    return Object.keys(userObj.user).length > 0
  }
  return false
}

export function fileToDataUrl (file) {
  const reader = new FileReader();
  const dataUrlPromise = new Promise((resolve, reject) => {
    reader.onerror = reject;
    reader.onload = () => resolve(reader.result);
  });
  reader.readAsDataURL(file);
  return dataUrlPromise;
}

export function formatTimeString (time) {
  const [year, month, day, hour, minute, second] = time.split(" ");
  const date = new Date(year, month - 1, day, hour, minute, second);
  const formattedDate = date.toLocaleString("en-US", {
    weekday: "short",
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "numeric",
    minute: "numeric",
    hour12: true,
  });

  return formattedDate
}