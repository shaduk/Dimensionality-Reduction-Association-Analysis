import numpy as np
import plotly
from plotly.graph_objs import *
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA



def preprocess(filename):
    inpdata = np.genfromtxt(filename,delimiter = '\t')
    col1 = []
    col2 = []
    for i in range(0, inpdata.shape[1]-1):
        col1.append(i)
    col2.append(inpdata.shape[1]-1)
    X = np.loadtxt(filename,delimiter = '\t', usecols = col1)
    labels = np.loadtxt(filename,delimiter = '\t', usecols = col2, dtype = 'S15')
    return X, labels

def runPCA(X):
    #find out mean of the data matrix
    means = []
    for i in range(0, len(X[0])):
        mean = np.mean(X[:,i])
        means.append(mean)
    means = np.array(means)
    print("The means matrix is : ")
    print(means) #print the mean matrix
    print(X-means)
    #find out the co-variance matrix
    cov_mat = np.dot(np.transpose(X - means),(X - means)) / (X.shape[0])
    print("The co-variance matrix is : ")
    print(cov_mat) #print the covariance matrix
    #find out the eigen values and eigen vectors
    eigen_val, eig_vector = np.linalg.eig(cov_mat)
    print("The eigen values are : ")
    print(eigen_val)
    print("The eigen vectors are : ")
    print(eig_vector)
    #Extract the indices of two highest eigen values
    top_two = sorted(range(len(eigen_val)), key=lambda i: eigen_val[i])[-2:]
    #make a pca matrix with two highest eigen vector
    pca_matrix = np.hstack(((eig_vector[:,top_two[0]].reshape(X.shape[1],1)), eig_vector[:,top_two[1]].reshape(X.shape[1],1)))

    print("Final Matrix: ", pca_matrix)
    #Calculate the Y matrix using the pca matrix
    Y = X.dot(pca_matrix)
    return Y


def runSVD(X):
    U, s, V = np.linalg.svd(X.T)
    print("SVD eigen vector: ")
    print(U)
    print(s)
    print(V)
    top_two = [1, 0]
     #make a pca matrix with two highest eigen vector
    svd_matrix = np.hstack(((U[:,top_two[0]].reshape(X.shape[1],1)), U[:,top_two[1]].reshape(X.shape[1],1)))
    print("Final Matrix: ", svd_matrix)
    #Calculate the Y matrix using the pca matrix
    Y = X.dot(svd_matrix)
    return Y

def runSNE(X):
    Y = TSNE(n_components=2).fit_transform(X)
    return Y

#This function draws the scatter plot. plotting code taken from plot.ly website
def draw_scatter_plot(Y, labels):
    unique_labels = set(labels)
    points = []
    for name in unique_labels:
        x = []
        y = []
        for i in range(0, len(labels)):
            if(labels[i] == name):
                x.append(Y[i,0])
                y.append(Y[i,1])
        x = np.array(x)
        y = np.array(y)
        point = Scatter(
            x = x,
            y = y,
            mode='markers',
            name=name,
            marker=Marker(size=12, line=Line(color='rgba(217, 154, 217, 123)',width=0.5),opacity=0.9))
        points.append(point)
    data = Data(points)
    layout = Layout(xaxis=XAxis(title='PC1', showline=True),
                    yaxis=YAxis(title='PC2', showline=True))
    fig = Figure(data=data, layout=layout)
    plotly.offline.plot(fig)
    
X, labels = preprocess("pca_b.txt")
print("Input dataset size rows: ")
print(X.shape[0])
print("Input dataset size columns: ")
print(X.shape[1])
Y_pca = runPCA(X)
draw_scatter_plot(Y_pca, labels)
# Y_tsne = runSNE(X)
# draw_scatter_plot(Y_tsne, labels)
# Y_svd = runSVD(X)
# draw_scatter_plot(Y_svd, labels)
